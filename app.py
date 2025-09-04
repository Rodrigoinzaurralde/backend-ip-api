# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 🔑 Clave secreta (usar variable de entorno en producción)
API_SECRET = os.environ.get("API_SECRET", "1234")


@app.route("/")
def home():
    return jsonify({"message": "API Flask corriendo ✅"})


@app.route("/mi-ip")
def mi_ip():
    """
    Devuelve la información de IP del usuario usando ip-api.com
    """
    xff = request.headers.get('X-Forwarded-For', '')
    ip = xff.split(',')[0] if xff else request.remote_addr

    url = f"http://ip-api.com/json/{ip}?fields=61439"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        data["ip"] = ip  # Agregamos la IP en la respuesta
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/guardar-usuario", methods=["POST"])
def guardar_usuario():
    """
    Guarda usuario, ciudad, país e IP en usuarios.txt (requiere API key).
    """
    try:
        api_key = request.headers.get("X-API-KEY")
        if api_key != API_SECRET:
            return jsonify({"status": "error", "message": "No autorizado"}), 401

        data = request.get_json()
        usuario = data.get("usuario", "desconocido")
        ciudad = data.get("ciudad", "sin_ciudad")
        pais = data.get("pais", "sin_pais")

        # 🔹 Obtener IP real
        xff = request.headers.get('X-Forwarded-For', '')
        ip = xff.split(',')[0] if xff else request.remote_addr

        with open("usuarios.txt", "a", encoding="utf-8") as f:
            f.write(f"Usuario: {usuario} | Ciudad: {ciudad} | País: {pais} | IP: {ip}\n")

        return jsonify({"status": "ok", "message": "Usuario guardado", "ip": ip})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/descargar-usuarios", methods=["GET"])
def descargar_usuarios():
    """
    Devuelve el archivo usuarios.txt como descarga (requiere API key).
    """
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_SECRET:
        return jsonify({"status": "error", "message": "No autorizado"}), 401

    try:
        return send_file("usuarios.txt", as_attachment=True)
    except FileNotFoundError:
        return jsonify({"usuarios": "Archivo vacío o no creado aún"})


@app.route("/borrar-usuarios", methods=["POST"])
def borrar_usuarios():
    """
    Borra el archivo usuarios.txt (requiere API key).
    """
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_SECRET:
        return jsonify({"status": "error", "message": "No autorizado"}), 401

    try:
        if os.path.exists("usuarios.txt"):
            os.remove("usuarios.txt")
            return jsonify({"status": "ok", "message": "Archivo usuarios.txt eliminado"})
        else:
            return jsonify({"status": "ok", "message": "El archivo ya no existe"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
