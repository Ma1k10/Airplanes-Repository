# Airplanes-Repositoty-

Este proyecto consiste en una **gestión de aerolínea** desarrollada con Django. A través de varias etapas, se han implementado funcionalidades clave para el manejo eficiente de vuelos, pasajeros y reservas.

## Etapas del Proyecto

### 1. Proyecto Base
- Primera versión con estructura inicial.
- Se identificaron problemas con la organización de carpetas y arquitectura del proyecto.

### 2. Mejoras y Nuevas Funcionalidades
- **Autenticación de usuarios:** Registro y login.
- **Registro de aviones:** Alta y gestión de aeronaves en el sistema.
- **Registro de pasajeros:**
  - Información personal (nombre, documento, contacto)
  - Historial de vuelos

### 3. Gestión de Reservas y Boletos
- **Visualización de disponibilidad de asientos** en los vuelos.
- **Reserva de asientos específicos** por parte de los pasajeros.
- **Gestión de estados de asientos:** disponible, reservado, ocupado.
- **Generación de boletos electrónicos** para los pasajeros.

## Tecnologías Utilizadas

- **Backend:** Django (Python)
- **Base de datos:** ( SQLite)
- **Frontend:** ( HTML)
  

## Instalación y Uso

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Ma1k10/Airplanes-Repository.git
   cd Airplanes-Repository
   ```
2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Ejecuta las migraciones:**
   ```bash
   python manage.py migrate
   ```
4. **Inicia el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

5. **Accede a la aplicación:**  
   Ve a [http://localhost:8000](http://localhost:8000) en tu navegador.

## Ejemplo de Uso

- Registro y login de usuarios
- Alta de aviones y pasajeros
- Reserva y visualización de asientos
- Generación de boletos electrónicos



## Autores

- [Ma1k10](https://github.com/Ma1k10)
- [ElArnold10](https://github.com/ElArnold10)

