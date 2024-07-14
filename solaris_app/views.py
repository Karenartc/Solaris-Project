from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CreateUserForm, PasswordResetForm, SetPasswordForm, CodeVerificationForm
from django.contrib.auth import authenticate, login as login_user, logout as logout_user, get_user_model
from .models import EnergyProduction, MaintenanceAlert, EnergyConsumption, CommunityEnergyTransaction, PasswordResetCode, CommunityMember, Community
from django.http import JsonResponse,  HttpResponse  
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from collections import defaultdict
import random
from django.db.models import Sum
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.db.models import Avg
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Importamos el modelo de usuario configurado en el proyecto
User = get_user_model()

#redirecciona a login
def homepage(request):
    """
    Redirecciona a la página de inicio de sesión.
    """
    return redirect('login')

#vista del login
def login(request):
    """
    Vista para gestionar el inicio de sesión de los usuarios.
    """
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            user = None
            username = None
        
        user = authenticate(request, username=username, password=password)
        if user is not None:         
            login_user(request, user)

            if login_user is not None and user.is_active:
                # Redirecciona al dashboard correspondiente según el rol del usuario
                if user.role == 'Propietario de vivienda':
                    return redirect('dashboard_propietario')
                elif user.role == 'Miembro de la comunidad':
                    return redirect('dashboard_comunidad')
                elif user.role == 'Administrador':
                    return redirect('dashboard_administrador')
                elif user.role == 'Inversor':
                    return redirect('dashboard_inversor')
                elif user.role == 'Usuario preocupado por el medio ambiente':
                    return redirect('dashboard_medio_ambiente')
                else:
                    messages.error(request, "Rol de usuario no reconocido")
            else:
                messages.error(request, "Correo electrónico o contraseña incorrectos")
        else:
            messages.error(request, "Correo electrónico o contraseña incorrectos")
    
    return render(request, 'auth/login.html')

# Cierra la sesión del usuario
def logout(request):
    """
    Cierra la sesión del usuario y redirecciona a la página de inicio de sesión.
    """
    logout_user(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('login')

# Vista para registrar nuevos usuarios
def register(request):
    """
    Vista para gestionar el registro de nuevos usuarios.
    """
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            storage = messages.get_messages(request)
            for _ in storage:
                pass
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CreateUserForm()
        
    context = {'form': form}
    return render(request, 'auth/register.html', context=context)

# Solicita el restablecimiento de la contraseña
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                    code = get_random_string(length=5)
                    PasswordResetCode.objects.create(user=user, code=code)
                    send_mail(
                        'Código de restablecimiento de contraseña',
                        f'Tu código de verificación es: {code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                    )
                    return redirect('password_reset_verify')
                else:
                    messages.error(request, "No existe una cuenta con este correo electrónico")
            except User.DoesNotExist:
                messages.error(request, 'No existe una cuenta con este correo electrónico.')
    else:
        form = PasswordResetForm()
    return render(request, 'auth/password/password_reset.html', {'form': form})

# Verifica el código de restablecimiento de contraseña
def password_reset_verify(request):
    if request.method == "POST":
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                reset_code = PasswordResetCode.objects.get(code=code)
                if reset_code.is_valid():
                    request.session['reset_user_id'] = reset_code.user.id
                    reset_code.delete()
                    return redirect('password_reset_confirm')
                else:
                    messages.error(request, 'El código ha expirado.')
                    reset_code.delete()
            except PasswordResetCode.DoesNotExist:
                messages.error(request, 'Código inválido.')
    else:
        form = CodeVerificationForm()
    return render(request, 'auth/password/password_reset_verify.html', {'form': form})

# Confirma el cambio de contraseña
def password_reset_confirm(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset_request')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('password_reset_request')

    if request.method == "POST":
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            del request.session['reset_user_id']
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente. Por favor inicia sesión con tu nueva contraseña.')
            return redirect('login') 
    else:
        form = SetPasswordForm()
    return render(request, 'auth/password/password_reset_confirm.html', {'form': form})


#HU01 - Dashboard del propietario
# mostrar gráficos en tiempo real de la producción de energía de los paneles solares, incluyendo datos 
# como la potencia generada, la energía acumulada y la eficiencia del sistema.
# alertas instantáneas en caso de que se detecten problemas en la producción de energía o se requiera mantenimiento, con 
# detalles específicos sobre la naturaleza del problema y las acciones recomendadas

# Simula datos de producción de energía y genera alertas de mantenimiento
def simulate_data(user):
    """
    Simula datos de producción de energía y genera alertas de mantenimiento.

    Parámetros:
    - user: Usuario para el cual se generarán los datos simulados y las alertas.
    """
    now = datetime.now()

    # Simular datos para el tiempo actual
    for i in range(5):  
        power_generated = random.uniform(0.2, 0.4) * (1 + random.uniform(-0.1, 0.1))   
        efficiency = random.uniform(0.15, 0.20)  
        time_exposed_to_sun = random.uniform(4, 8)  
        accumulated_energy = power_generated * time_exposed_to_sun  
        timestamp = now

        # Crear un registro de producción de energía con datos simulados
        energy_production = EnergyProduction.objects.create(
            user=user,
            power_generated=power_generated,
            accumulated_energy=accumulated_energy,
            efficiency=efficiency,
            timestamp=timestamp,
        )

    # Generar una alerta de producción de energía
    power_generated = random.uniform(0.2, 0.4) * (1 + random.uniform(-0.1, 0.1)) * 1000 
    efficiency = random.uniform(0.15, 0.20)
    time_exposed_to_sun = random.uniform(4, 8) 
    accumulated_energy = power_generated * time_exposed_to_sun / 1000  
    timestamp = now

    # Generar alertas según las condiciones simuladas
    alert_generated = False

    # Alerta por baja eficiencia
    if efficiency < 0.16:
        alert_message = "Eficiencia del sistema baja. Requiere mantenimiento."
        alert = MaintenanceAlert.objects.create(
            user=user,
            title="Baja Eficiencia",
            message=alert_message,
            timestamp=timestamp,
            energy_production=energy_production,
        )
        alert_generated = True

    # Alerta por baja producción de energía
    if power_generated < 0.25 * 1000:
        alert_message = "Producción de energía baja. Verifique los paneles."
        alert = MaintenanceAlert.objects.create(
            user=user,
            title="Baja Producción de Energía",
            message=alert_message,
            timestamp=timestamp,
            energy_production=energy_production,
        )
        alert_generated = True

    # Alerta por temperatura del panel elevada (simulada)
    panel_temperature = random.uniform(20, 100)  # Temperatura en grados Celsius
    if panel_temperature > 80:
        alert_message = f"Temperatura del panel elevada: {panel_temperature:.2f}°C. Riesgo de daño."
        alert = MaintenanceAlert.objects.create(
            user=user,
            title="Alta Temperatura del Panel",
            message=alert_message,
            timestamp=timestamp,
            energy_production=energy_production,
        )
        alert_generated = True

    # Alerta por baja exposición al sol
    if time_exposed_to_sun < 5:
        alert_message = "Baja exposición al sol. Potencial de energía reducido."
        alert = MaintenanceAlert.objects.create(
            user=user,
            title="Baja Exposición al Sol",
            message=alert_message,
            timestamp=timestamp,
            energy_production=energy_production,
        )
        alert_generated = True

    # Si ninguna alerta se generó, agregar una alerta de estado normal
    if not alert_generated:
        alert_message = "El sistema funciona correctamente. Sin alertas."
        MaintenanceAlert.objects.create(
            user=user,
            title="Estado Normal",
            message=alert_message,
            timestamp=timestamp,
        )

@login_required
def dashboard_propietario(request):
    """
    Vista para el dashboard del propietario. Muestra gráficos en tiempo real de la producción de energía
    y alertas instantáneas en caso de problemas o requerimientos de mantenimiento.
    """
    user = request.user
    simulate_data(user) 

    # Obtener los últimos 20 registros
    energy_production_data = EnergyProduction.objects.all().order_by('-timestamp')[:20]
    # Obtener las últimas 10 alertas de mantenimiento
    maintenance_alerts = MaintenanceAlert.objects.filter(user=request.user).order_by('-timestamp')[:10]

    # Formatear los timestamps de las alertas de mantenimiento
    for alert in maintenance_alerts:
        alert.timestamp = alert.timestamp.strftime("%d %B %Y %I:%M %p")

    context = {
        'user': request.user,
        'energy_production_data': energy_production_data,
        'maintenance_alerts': maintenance_alerts,
    }
    return render(request, 'dashboard/propietario/dashboard_propietario.html', context)

# Vista para obtener los últimos datos 
@login_required
def get_latest_data(request):
    """
    Vista para obtener los últimos datos de producción de energía en formato JSON.
    """
    latest_data = EnergyProduction.objects.filter(user=request.user).order_by('-timestamp')[:20]
    data = []
    for record in latest_data:
        data.append({
            'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'accumulated_energy': round(record.accumulated_energy, 2),
            'efficiency': round(record.efficiency, 2),
            'power_generated': round(record.power_generated, 2),
        })
    return JsonResponse(data, safe=False)

# Vista para la página con todos los datos
@login_required
def energy_data_full(request):
    """
    Vista para mostrar la página con todos los datos de producción de energía.
    """
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard/propietario/energy_data_full.html', context)

# Vista para obtener todos los datos
@login_required
def get_all_data(request):
    """
    Vista para obtener todos los datos de producción de energía en formato JSON.
    """
    all_data = EnergyProduction.objects.filter(user=request.user).order_by('timestamp')
    data = []
    for record in all_data:
        data.append({
            'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'accumulated_energy': round(record.accumulated_energy, 2),
            'efficiency': round(record.efficiency, 2),
            'power_generated': round(record.power_generated, 2),
        })
    data.reverse()  
    return JsonResponse(data, safe=False)


#HU02 - Dashboard de la comunidad
# Consumo de energía personal, desglosado por horas, días, semanas y meses
# Información sobre la contribución de energía a la red comunitaria, con métricas como la cantidad de energía 
# compartida, los ahorros generados y el impacto ambiental positivo.
def simulate_energy_data(user):
    """
    Simula datos de consumo de energía para un usuario y transacciones de energía para la red comunitaria.
    """
    now = timezone.now()
    existing_data_count = EnergyConsumption.objects.filter(user=user).count()

    # Si no hay ningún dato para el usuario registrado, se crearán 30 datos aleatorios.
    if existing_data_count == 0:
        for _ in range(30):
            random_date = now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            consumption_amount = random.uniform(0.1, 5.0)  # kWh
            EnergyConsumption.objects.create(
                user=user,
                amount=consumption_amount,
                timestamp=random_date,
            )
    else:
        # Si ya hay datos para el usuario, se verificará si la fecha cambió desde la última entrada.
        latest_record = EnergyConsumption.objects.filter(user=user).latest('timestamp')
        latest_date = latest_record.timestamp.date()

        # Si la fecha ha cambiado desde la última entrada, se crearán datos nuevos para el día actual.
        if latest_date < now.date():
            for hour in range(24):
                consumption_amount = random.uniform(0.1, 5.0) 
                timestamp = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                EnergyConsumption.objects.create(
                    user=user,
                    amount=consumption_amount,
                    timestamp=timestamp,
                )
        else:
            # Si se vuelve a llamar a la función y no se cumplen los parámetros anteriores, se crearán 5 datos aleatorios.
            for _ in range(5):
                random_date = now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
                consumption_amount = random.uniform(0.1, 5.0)  # kWh
                EnergyConsumption.objects.create(
                    user=user,
                    amount=consumption_amount,
                    timestamp=random_date,
                )

def simulate_transaction_data(user):
    """
    Simula transacciones de energía para la red comunitaria.
    """
    now = timezone.now()
    existing_data_count = CommunityEnergyTransaction.objects.filter(from_user=user).count()
    all_users = list(User.objects.exclude(id=user.id))

    # Si no hay ningún dato para el usuario registrado, se crearán 30 datos aleatorios.
    if existing_data_count == 0:
        for _ in range(30):
            if not all_users:
                break
            to_user = random.choice(all_users)
            random_date = now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            transaction_amount = random.uniform(0.1, 5.0)  # kWh
            CommunityEnergyTransaction.objects.create(
                from_user=user,
                to_user=to_user,
                amount=transaction_amount,
                timestamp=random_date,
            )
    else:
        # Si ya hay datos para el usuario, se verificará si la fecha cambió desde la última entrada.
        latest_record = CommunityEnergyTransaction.objects.filter(from_user=user).latest('timestamp')
        latest_date = latest_record.timestamp.date()

        # Si la fecha ha cambiado desde la última entrada, se crearán datos nuevos para el día actual.
        if latest_date < now.date():
            for hour in range(24):
                if not all_users:
                    break
                to_user = random.choice(all_users)
                transaction_amount = random.uniform(0.1, 5.0)  # kWh
                timestamp = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                CommunityEnergyTransaction.objects.create(
                    from_user=user,
                    to_user=to_user,
                    amount=transaction_amount,
                    timestamp=timestamp,
                )
        else:
            # Si se vuelve a llamar a la función y no se cumplen los parámetros anteriores, se crearán 5 datos aleatorios.
            for _ in range(5):
                if not all_users:
                    break
                to_user = random.choice(all_users)
                random_date = now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
                transaction_amount = random.uniform(0.1, 5.0)  # kWh
                CommunityEnergyTransaction.objects.create(
                    from_user=user,
                    to_user=to_user,
                    amount=transaction_amount,
                    timestamp=random_date,
                )

@login_required
def dashboard_comunidad(request):
    """
    Vista para el dashboard de la comunidad. Muestra el consumo de energía personal y la contribución a la red comunitaria.
    """
    user = request.user
    simulate_energy_data(user)
    simulate_transaction_data(user)

    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_month = now.replace(day=1)

    daily_consumption = EnergyConsumption.objects.filter(user=user, timestamp__gte=start_of_day)
    weekly_consumption = EnergyConsumption.objects.filter(user=user, timestamp__gte=start_of_week)
    monthly_consumption = EnergyConsumption.objects.filter(user=user, timestamp__gte=start_of_month)

    daily_total = daily_consumption.aggregate(total=Sum('amount'))['total'] or 0
    weekly_total = weekly_consumption.aggregate(total=Sum('amount'))['total'] or 0
    monthly_total = monthly_consumption.aggregate(total=Sum('amount'))['total'] or 0

    transactions = CommunityEnergyTransaction.objects.filter(from_user=user).order_by('-timestamp')
    transactions_by_user = defaultdict(list)
    for transaction in transactions:
        transactions_by_user[transaction.to_user].append(transaction)

    total_energy_shared = transactions.aggregate(total=Sum('amount'))['total'] or 0
    savings_generated = total_energy_shared * 0.10
    environmental_impact = total_energy_shared * 0.5

    context = {
        'user': user,
        'daily_total': daily_total,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'daily_consumption': daily_consumption,
        'weekly_consumption': weekly_consumption,
        'monthly_consumption': monthly_consumption,
        'transactions_by_user': transactions_by_user,
        'total_energy_shared': total_energy_shared,
        'savings_generated': savings_generated,
        'environmental_impact': environmental_impact,
    }

    return render(request, 'dashboard/comunidad/dashboard_comunidad.html', context)

@login_required
def get_latest_energy_data(request):
    """
    Vista para obtener los últimos datos de consumo de energía y transacciones de energía en formato JSON
    """
    
    latest_consumption = EnergyConsumption.objects.filter(user=request.user).order_by('-timestamp')[:20]
    latest_transactions = CommunityEnergyTransaction.objects.filter(from_user=request.user).order_by('-timestamp')[:20]

    consumption_data = [{'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'amount': round(record.amount, 2)} for record in latest_consumption]
    transaction_data = [{'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'amount': round(record.amount, 2)} for record in latest_transactions]

    data = {
        'consumption': consumption_data,
        'transactions': transaction_data,
    }

    return JsonResponse(data, safe=False)

@login_required
def get_all_energy_data(request):
    """
    Vista para obtener todos los datos de consumo de energía y transacciones de energía en formato JSON
    """
    all_consumption = EnergyConsumption.objects.filter(user=request.user).order_by('timestamp')
    all_transactions = CommunityEnergyTransaction.objects.filter(from_user=request.user).order_by('timestamp')

    consumption_data = [{'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'amount': round(record.amount, 2)} for record in all_consumption]
    transaction_data = [{'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'amount': round(record.amount, 2)} for record in all_transactions]

    data = {
        'consumption': consumption_data,
        'transactions': transaction_data,
    }

    return JsonResponse(data, safe=False)

@login_required
def daily_consumption_detail(request):
    """
    Vista para mostrar el detalle del consumo diario de energía.
    """
    user = request.user
    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_consumption = EnergyConsumption.objects.filter(user=user, timestamp__gte=start_of_day)

    context = {
        'daily_consumption': daily_consumption,
    }
    return render(request, 'dashboard/comunidad/daily_consumption_detail.html', context)

@login_required
def weekly_consumption_detail(request):
    """
    Vista para mostrar el detalle del consumo semanal de energía.
    """
    user = request.user
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())
    weekly_consumption = EnergyConsumption.objects.filter(user=user, timestamp__gte=start_of_week)
    context = {
        'weekly_consumption': weekly_consumption,
    }
    return render(request, 'dashboard/comunidad/weekly_consumption_detail.html', context)

@login_required
def monthly_consumption_detail(request):
    """
    Vista para mostrar el detalle del consumo mensual de energía.
    """
    user = request.user
    now = timezone.now()
    start_of_month = now.replace(day=1)
    monthly_consumption = EnergyConsumption.objects.filter(user=user, timestamp__gte=start_of_month)
    context = {
        'monthly_consumption': monthly_consumption,
    }
    return render(request, 'dashboard/comunidad/monthly_consumption_detail.html', context)


#HU03 - Dashboard del administrador
# panel de control centralizado para supervisar el estado operativo de todos los sistemas solares de cada propietario.
# Herramientas de gestión de usuarios para agregar, modificar o eliminar usuarios y gestionar permisos de acceso.
# informes mensuales detallados sobre el rendimiento de la red, incluyendo métricas clave 
# como el consumo total de energía

@login_required
def dashboard_administrador(request):
    """
    Vista para el dashboard del administrador. Muestra el estado operativo de los sistemas solares de cada propietario,
    herramientas de gestión de usuarios y un informe mensual detallado sobre el rendimiento de la red.
    """

    # Obtener todos los usuarios propietarios de vivienda
    homeowners = User.objects.filter(role='Propietario de vivienda', is_active=True)  
    
    # Obtener datos de producción de energía y alertas para cada propietario
    data = []
    for homeowner in homeowners:
        energy_production_data = EnergyProduction.objects.filter(user=homeowner).order_by('-timestamp')[:20]
        maintenance_alerts = MaintenanceAlert.objects.filter(user=homeowner).order_by('-timestamp')[:10]

        total_energy = sum([ep.accumulated_energy for ep in energy_production_data])
        avg_efficiency = sum([ep.efficiency for ep in energy_production_data]) / len(energy_production_data) if energy_production_data else 0
        total_power_generated = sum([ep.power_generated for ep in energy_production_data])

        data.append({
            'homeowner': homeowner,
            'energy_production_data': energy_production_data,
            'maintenance_alerts': maintenance_alerts,
            'total_energy': total_energy,
            'avg_efficiency': avg_efficiency,
            'total_power_generated': total_power_generated,
        })
    
    # Obtener todos los usuarios activos para la tabla de gestión de usuarios
    all_users = User.objects.filter(is_active=True)

    context = {
        'data': data,
        'all_users': all_users,
    }
    return render(request, 'dashboard/administrador/dashboard_administrador.html', context)

@login_required
def detalles_propietario(request, homeowner_id):
    """ 
    Vista para mostrar los detalles de un propietario de vivienda específico.
    """
    homeowner = get_object_or_404(User, id=homeowner_id, role='Propietario de vivienda')
    
    energy_production_data = EnergyProduction.objects.filter(user=homeowner).order_by('-timestamp')
    maintenance_alerts = MaintenanceAlert.objects.filter(user=homeowner).order_by('-timestamp')

    context = {
        'homeowner': homeowner,
        'energy_production_data': energy_production_data,
        'maintenance_alerts': maintenance_alerts,
    }
    return render(request, 'dashboard/administrador/detalles_propietario.html', context)

@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'dashboard/administrador/user_list.html', {'users': users})

def manage_user(request, user_id=None):
    is_edit_mode = user_id is not None
    if is_edit_mode:
        user = get_object_or_404(User, id=user_id)
        form = CreateUserForm(request.POST or None, instance=user)
    else:
        form = CreateUserForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f"{'Modificación' if is_edit_mode else 'Registro'} exitoso.")
            return redirect('dashboard_administrador')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    context = {'form': form, 'is_edit_mode': is_edit_mode}
    return render(request, 'dashboard/administrador/manage_user.html', context)

@login_required
def delete_user(request, user_id):
    """ 
    Vista para desactivar un usuario.
    """
    user = get_object_or_404(User, id=user_id)
    
    # Cambiar el estado is_active a False en lugar de eliminar físicamente
    user.is_active = False
    user.role = " " 
    user.save()

    messages.success(request, "Usuario desactivado exitosamente.")
    return redirect('dashboard_administrador')

@login_required
def informe_mensual(request):
    """ 
    Vista para generar un informe mensual detallado sobre el rendimiento de la red.
    """
    # Calcular el total de producción de energía para propietarios de vivienda
    propietarios_vivienda = User.objects.filter(role='Propietario de vivienda')

    total_potencia_generada = EnergyProduction.objects.filter(user__in=propietarios_vivienda).aggregate(total_potencia=Sum('power_generated'))['total_potencia'] or 0
    total_energia_acumulada = EnergyProduction.objects.filter(user__in=propietarios_vivienda).aggregate(total_energia=Sum('accumulated_energy'))['total_energia'] or 0
    eficiencia_promedio = EnergyProduction.objects.filter(user__in=propietarios_vivienda).aggregate(avg_eficiencia=Avg('efficiency'))['avg_eficiencia'] or 0
    
    context = {
        'total_potencia_generada': total_potencia_generada,
        'total_energia_acumulada': total_energia_acumulada,
        'eficiencia_promedio': eficiencia_promedio,
    }

    return render(request, 'dashboard/administrador/informe_mensual.html', context)

@login_required
def generar_pdf(request):
    """ 
    Vista para generar un informe mensual detallado sobre el rendimiento de la red en formato PDF.
    """
    # Obtener datos necesarios para el informe PDF
    propietarios_vivienda = User.objects.filter(role='Propietario de vivienda')
    
    total_potencia_generada = EnergyProduction.objects.filter(user__in=propietarios_vivienda).aggregate(total=Sum('power_generated'))['total'] or 0
    total_energia_acumulada = EnergyProduction.objects.filter(user__in=propietarios_vivienda).aggregate(total=Sum('accumulated_energy'))['total'] or 0
    eficiencia_promedio = EnergyProduction.objects.filter(user__in=propietarios_vivienda).aggregate(avg=Avg('efficiency'))['avg'] or 0
    
    context = {
        'total_potencia_generada': total_potencia_generada,
        'total_energia_acumulada': total_energia_acumulada,
        'eficiencia_promedio': eficiencia_promedio,
    }

    # Renderizar la plantilla con los datos
    template_path = 'dashboard/administrador/informe_mensual_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_mensual.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Hubo un error al generar el PDF', status=400)
    return response


#HU04 - Dashboard del usuario preocupado por el medio ambiente
# informes mensuales detallados sobre ingresos y crecimientos del negocio Solaris, desglosados por fuentes de ingresos como la 
# venta de energía, la participación en la red comunitaria y las tarifas de conexión

def calculate_monthly_income(request):
    """ 
    Función para calcular los ingresos mensuales y crecimiento del negocio Solaris
    """
    current_month = datetime.now().month

    # Calcular ingresos mensuales de la comunidad por tipo de transacción para todos los usuarios
    transactions = CommunityEnergyTransaction.objects.filter(timestamp__month=current_month)
    
    total_energy_sales = transactions.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
    total_community_participation = transactions.aggregate(total_participation=Sum('amount'))['total_participation'] or 0.0
    total_connection_fees = transactions.aggregate(total_fees=Sum('amount'))['total_fees'] or 0.0

    # Calcular ingresos mensuales de producción de energía para todos los usuarios
    energy_productions = EnergyProduction.objects.filter(timestamp__month=current_month)
    
    total_power_generated = energy_productions.aggregate(total_power=Sum('power_generated'))['total_power'] or 0.0
    total_accumulated_energy = energy_productions.aggregate(total_energy=Sum('accumulated_energy'))['total_energy'] or 0.0

    return {
        'total_energy_sales': total_energy_sales,
        'total_community_participation': total_community_participation,
        'total_connection_fees': total_connection_fees,
        'total_power_generated': total_power_generated,
        'total_accumulated_energy': total_accumulated_energy,
    }

@login_required
def dashboard_medio_ambiente(request):
    """ 
    Vista para el dashboard del usuario preocupado por el medio ambiente.
    """
    income_data = calculate_monthly_income(request)
    return render(request, 'dashboard/medioAmbiente/dashboard_medio_ambiente.html', {'income_data': income_data})

@login_required
def generate_pdf_medioAmbiente(request):
    """ 
    Vista para generar un informe mensual detallado sobre ingresos y crecimiento del negocio Solaris en formato PDF.
        """
    # Obtener los datos del ingreso mensual
    income_data = calculate_monthly_income(request)
    
    # Renderizar la plantilla HTML con los datos
    template_path = 'dashboard/medioAmbiente/informe_medio_ambiente_pdf.html'
    context = {'income_data': income_data}
    html = render_to_string(template_path, context)
    
    # Crear un archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="dashboard_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Si hay un error, devolver un mensaje de error
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF')
    
    return response


#HU05 - Dashboard del inversor
# enviar informes mensuales detallados sobre el impacto ambiental del proyecto Solaris, incluyendo datos 
# como la cantidad de energía renovable generada, las emisiones de CO2 evitadas y los árboles equivalentes plantados.

def calculate_environmental_impact():
    """ 
    Función para calcular el impacto ambiental del proyecto
    """
    # Calcular energía renovable generada
    renewable_energy_generated = EnergyProduction.objects.aggregate(total_power=Sum('power_generated')).get('total_power', 0)
    
    # Calcular emisiones de CO2 evitadas (asumiendo 0.1 Kg CO2 por kWh generado)
    co2_emissions_avoided = renewable_energy_generated * 0.1 if renewable_energy_generated else 0
    
    # Calcular árboles equivalentes plantados (asumiendo 5 Kg CO2 equivalen a plantar 1 árbol)
    trees_planted_equivalent = co2_emissions_avoided / 5 if co2_emissions_avoided else 0
    
    return {
        'renewable_energy_generated': renewable_energy_generated,
        'co2_emissions_avoided': co2_emissions_avoided,
        'trees_planted_equivalent': trees_planted_equivalent
    }

def dashboard_inversor(request):
    """ 
    Vista para el dashboard del inversor.
    """
    # Obtener datos de producción de energía
    energy_production = EnergyProduction.objects.filter(user=request.user)
    
    # Calcular impacto ambiental utilizando la función previamente definida
    environmental_impact = calculate_environmental_impact()
    
    context = {
        'energy_production': energy_production,
        'environmental_impact': environmental_impact,
    }
    
    return render(request, 'dashboard/inversor/dashboard_inversor.html', context)

def render_to_pdf_inversor(template_src, context_dict):
    """ 
    Función para renderizar un template HTML a PDF.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # Crear el PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def download_dashboard_inversor_pdf(request):
    """ 
    Vista para descargar un informe mensual detallado sobre el impacto ambiental del proyecto Solaris en formato PDF.
    """
    # Obtener datos de producción de energía y calcular impacto ambiental
    energy_production = EnergyProduction.objects.filter(user=request.user)
    environmental_impact = calculate_environmental_impact()

    # Contexto para el template HTML
    context = {
        'energy_production': energy_production,
        'environmental_impact': environmental_impact,
    }

    # Renderizar el template a PDF y devolver la respuesta HTTP
    pdf = render_to_pdf_inversor('dashboard/inversor/dashboard_inversor_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="dashboard_inversor.pdf"'
        return response
    return HttpResponse("Error al generar el PDF", status=400)

