# API Flask para obtener información de IP

Esta API construida con Flask permite obtener información geográfica de una IP pública, útil para proyectos de geolocalización o análisis de tráfico.

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo
   ```

2. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

## Uso

Ejecuta el servidor localmente:
```sh
python app.py
```
Por defecto corre en el puerto `5001`.

### Endpoints

- `/`  
  Retorna mensaje de bienvenida.

- `/mi-ip`  
  Retorna información geográfica de la IP detectada.

## Despliegue

Puedes desplegar esta API en servicios como Render, Heroku, etc.

## Requisitos

- Python 3.7+
- Flask
- Flask-CORS
- Requests
- Gunicorn (opcional para producción)

## Licencia

MIT
