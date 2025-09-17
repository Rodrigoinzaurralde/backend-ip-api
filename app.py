# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

API_SECRET = os.environ.get("API_SECRET", "1234")
USUARIOS_FILE = "usuarios.txt"


@app.route("/")
def home():
    return jsonify({"message": "API Flask corriendo ✅"})


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

        with open(USUARIOS_FILE, "a", encoding="utf-8") as f:
            f.write(
                f"Usuario: {usuario} | Ciudad: {ciudad} | País: {pais} | IP: {ip} | Latitud: {lat} | Longitud : {long}\n"
            )

        return jsonify({
            "status": "ok",
            "message": "Usuario guardado",
            "ip": ip
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
        return send_file(USUARIOS_FILE, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"usuarios": "Archivo vacío o no creado aún"})


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
    app.run(host="0.0.0.0", port=port)
