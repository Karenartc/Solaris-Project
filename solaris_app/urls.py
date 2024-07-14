from django.urls import path
from . import views

urlpatterns = [
    # Página de inicio
    path('', views.homepage, name=''),

    # Autenticación
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Recuperación de contraseña 
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password_reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    # Paneles de control específicos
    path('dashboard_propietario/', views.dashboard_propietario, name='dashboard_propietario'),
    path('dashboard_comunidad/', views.dashboard_comunidad, name='dashboard_comunidad'),
    path('dashboard_administrador/', views.dashboard_administrador, name='dashboard_administrador'),
    path('dashboard_inversor/', views.dashboard_inversor, name='dashboard_inversor'),
    path('dashboard_medio_ambiente/', views.dashboard_medio_ambiente, name='dashboard_medio_ambiente'),

    #HU01 PROPIETARIO
    path('get-latest-data/', views.get_latest_data, name='get_latest_data'),
    path('energy_data_full/', views.energy_data_full, name='energy_data_full'),
    path('get_all_data/', views.get_all_data, name='get_all_data'),

    #HU02 COMUNIDAD
    path('get-latest-energy-data/', views.get_latest_energy_data, name='get_latest_energy_data'),
    path('get-all-energy-data/', views.get_all_energy_data, name='get_all_energy_data'),
    path('daily_consumption/', views.daily_consumption_detail, name='daily_consumption_detail'),
    path('weekly_consumption/', views.weekly_consumption_detail, name='weekly_consumption_detail'),
    path('monthly_consumption/', views.monthly_consumption_detail, name='monthly_consumption_detail'),

    #HU03 ADMINISTRADOR
    path('detalles_propietario/<int:homeowner_id>/', views.detalles_propietario, name='detalles_propietario'),
    path('users/', views.user_list, name='user_list'),
    path('usuario/agregar/', views.manage_user, name='add_user'),
    path('usuario/modificar/<int:user_id>/', views.manage_user, name='edit_user'),
    path('usuario/eliminar/<int:user_id>/', views.delete_user, name='delete_user'),
    path('informe_mensual/', views.informe_mensual, name='informe_mensual'),
    path('generar_pdf/', views.generar_pdf, name='generar_pdf'),

    #HU04 INVERSOR
    path('generate_pdf/', views.generate_pdf_medioAmbiente, name='generate_pdf_medioAmbiente'),

    #HU05 MEDIO AMBIENTE
    path('download-pdf/', views.download_dashboard_inversor_pdf, name='download_dashboard_inversor_pdf'),
]

