Proyecto Solaris

El Proyecto Solaris es un aplicativo web desarrollado en Django para la gestión de producción y consumo de energía solar, así como para la administración de redes comunitarias de energía. La aplicación permite a los propietarios de sistemas solares, miembros de la comunidad, administradores e inversores visualizar y gestionar información relevante a través de dashboards personalizados.

Características
Dashboard del Propietario
- Visualización en tiempo real de la producción de energía de los paneles solares.
- Gráficos con datos de potencia generada, energía acumulada y eficiencia del sistema.
- Alertas instantáneas en caso de problemas en la producción de energía o necesidad de mantenimiento.

Dashboard de la Comunidad
- Información del consumo de energía personal, desglosado por horas, días, semanas y meses.
- Detalles sobre la contribución de energía a la red comunitaria.
- Métricas de ahorro e impacto ambiental positivo.

Dashboard del Administrador
- Panel de control centralizado para supervisar el estado operativo de todos los sistemas solares.
- Herramientas de gestión de usuarios y permisos de acceso.
- Informe detalladoe sobre el rendimiento de la red.

Dashboard del Usuario Preocupado por el Medio Ambiente
- Informe sobre ingresos y crecimiento del negocio Solaris.
- Desglose por fuentes de ingresos: venta de energía, participación en la red comunitaria y tarifas de conexión.

Dashboard del Inversor
- Informe sobre el impacto ambiental del proyecto Solaris.
- Datos sobre energía renovable generada, emisiones de CO2 evitadas y árboles equivalentes plantados.

nstalación

Prerrequisitos
- Python 3.11
- MySQL
- HeidiSQL (opcional)
- Virtualenv

Pasos para la instalación
1. Clona el repositorio:
    git clone https://github.com/tuusuario/solaris.git

2. Crea y activa un entorno virtual:
    cd solaris
    python -m venv venv
    source venv/bin/activate o En Windows usa: venv\Scripts\activate

3. Instala las dependencias:
    pip install -r requirements.txt

4. Configura la base de datos en `config.py` con tus credenciales de MySQL.
5. Aplica las migraciones:
    python manage.py migrate

7. Ejecuta el servidor de desarrollo:
    python manage.py runserver

Uso

Acceso al Panel de Administración
Accede a http://127.0.0.1:8000/ crea un usuario e inicia sesión.

Configuración de Dashboards
- Propietario: Registra sistemas solares y visualiza datos de producción.
- Comunidad: Visualiza el consumo y contribución de energía comunitaria.
- Administrador: Supervisa todos los sistemas y gestiona usuarios.
- Usuario Preocupado por el Medio Ambiente:** Recibe informes de ingresos y crecimiento.
- Inversor: Recibe informes de impacto ambiental.

¡Gracias por usar Solaris!