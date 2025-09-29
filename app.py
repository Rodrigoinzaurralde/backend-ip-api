# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import os
import threading
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

API_SECRET = os.environ.get("API_SECRET", "1234")
USUARIOS_FILE = "usuarios.txt"

# URL de aplicacion en render 
APP_URL = os.environ.get("APP_URL", "https://backend-ip-api.onrender.com/mi-ip")

def keep_alive():
    """
    Función que se ejecuta en un hilo separado para mantener la app activa
    """
    while True:
        try:
            # Espera 12 minutos (720 segundos)
            time.sleep(720)
            
            # Hace una petición a sí misma
            if APP_URL != "https://tu-app.onrender.com":
                response = requests.get(f"{APP_URL}/", timeout=10)
                print(f"Keep-alive ping: {response.status_code}")
        except Exception as e:
            print(f"Error en keep-alive: {e}")

# Iniciar el hilo de keep-alive solo en producción
if os.environ.get("RENDER"):
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    print("🚀 Keep-alive iniciado")

@app.route("/")
def home():
    return jsonify({
        "message": "API Flask corriendo ✅",
        "status": "active",
        "timestamp": time.time()
    })

@app.route("/health")
def health():
    """
    Endpoint específico para health checks
    """
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    })

@app.route("/mi-ip")
def mi_ip():
    """
    Devuelve información de geolocalización según la IP del visitante.
    """
    xff = request.headers.get('X-Forwarded-For', '')
    ip = xff.split(',')[0] if xff else request.remote_addr
    url = f"http://ip-api.com/json/{ip}?fields=61439"
    
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        data["ip"] = ip
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/guardar-usuario", methods=["POST"])
def guardar_usuario():
    try:
        data = request.get_json()
        usuario = data.get("usuario", "desconocido")
        ciudad = data.get("ciudad", "sin_ciudad")
        pais = data.get("pais", "sin_pais")
        lat = data.get("lat", "sin_lat")
        long = data.get("long", "sin_long")
        
        # Capturar IP real
        xff = request.headers.get('X-Forwarded-For', '')
        ip = xff.split(',')[0] if xff else request.remote_addr
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(USUARIOS_FILE) if os.path.dirname(USUARIOS_FILE) else '.', exist_ok=True)
        
        with open(USUARIOS_FILE, "a", encoding="utf-8") as f:
            f.write(
                f"Usuario: {usuario} | Ciudad: {ciudad} | País: {pais} | IP: {ip} | Latitud: {lat} | Longitud: {long} | Timestamp: {time.time()}\n"
            )
            
        return jsonify({
            "status": "ok",
            "message": "Usuario guardado",
            "ip": ip,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/descargar-usuarios", methods=["GET"])
def descargar_usuarios():
    """
    Endpoint privado para descargar todos los usuarios guardados.
    """
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_SECRET:
        return jsonify({"status": "error", "message": "No autorizado"}), 401
    
    try:
        if os.path.exists(USUARIOS_FILE):
            return send_file(USUARIOS_FILE, as_attachment=True)
        else:
            # Crear archivo vacío si no existe
            with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
                f.write("# Archivo de usuarios creado automáticamente\n")
            return send_file(USUARIOS_FILE, as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/borrar-usuarios", methods=["POST"])
def borrar_usuarios():
    """
    Endpoint privado para borrar el archivo usuarios.txt
    """
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_SECRET:
        return jsonify({"status": "error", "message": "No autorizado"}), 401
    
    try:
        if os.path.exists(USUARIOS_FILE):
            os.remove(USUARIOS_FILE)
            return jsonify({
                "status": "ok",
                "message": "Archivo usuarios.txt eliminado"
            })
        else:
            return jsonify({
                "status": "ok", 
                "message": "El archivo ya no existe"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)