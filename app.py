# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

API_SECRET = os.environ.get("API_SECRET", "1234")

rate_limit = {}
REDIRECT_URL = "https://rodrigoinzaurralde.github.io/eMercado/error.html"
WAIT_SECONDS = 5
USUARIOS_FILE = "usuarios.txt"

@app.before_request
def limit_remote_addr():
    xff = request.headers.get('X-Forwarded-For', '')
    ip = xff.split(',')[0] if xff else request.remote_addr
    now = time.time()
    last = rate_limit.get(ip, 0)
    if now - last < 1:
        return jsonify({
            "redirect_url": REDIRECT_URL,
            "wait_seconds": WAIT_SECONDS
        }), 429
    rate_limit[ip] = now


@app.route("/")
def home():
    return jsonify({"message": "API Flask corriendo ✅"})


@app.route("/mi-ip")
def mi_ip():
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


@app.route("/registrar-visita", methods=["POST"])
def registrar_visita():
    try:
        data = request.get_json()
        usuario = str(data.get("usuario", "desconocido"))[:50]
        ciudad = str(data.get("ciudad", "sin_ciudad"))[:50]
        pais = str(data.get("pais", "sin_pais"))[:50]

        xff = request.headers.get('X-Forwarded-For', '')
        ip = xff.split(',')[0] if xff else request.remote_addr

        with open(USUARIOS_FILE, "a", encoding="utf-8") as f:
            f.write(f"Usuario: {usuario} | Ciudad: {ciudad} | País: {pais} | IP: {ip}\n")

        return jsonify({"status": "ok", "message": "Visita registrada", "ip": ip})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/guardar-usuario", methods=["POST"])
def guardar_usuario():
    try:
        api_key = request.headers.get("X-API-KEY")
        if api_key != API_SECRET:
            return jsonify({"status": "error", "message": "No autorizado"}), 401

        data = request.get_json()
        usuario = data.get("usuario", "desconocido")
        ciudad = data.get("ciudad", "sin_ciudad")
        pais = data.get("pais", "sin_pais")
        xff = request.headers.get('X-Forwarded-For', '')
        ip = xff.split(',')[0] if xff else request.remote_addr

        with open(USUARIOS_FILE, "a", encoding="utf-8") as f:
            f.write(f"Usuario: {usuario} | Ciudad: {ciudad} | País: {pais} | IP: {ip}\n")

        return jsonify({"status": "ok", "message": "Usuario guardado", "ip": ip})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/descargar-usuarios", methods=["GET"])
def descargar_usuarios():
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_SECRET:
        return jsonify({"status": "error", "message": "No autorizado"}), 401

    try:
        return send_file(USUARIOS_FILE, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"usuarios": "Archivo vacío o no creado aún"})


@app.route("/borrar-usuarios", methods=["POST"])
def borrar_usuarios():
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_SECRET:
        return jsonify({"status": "error", "message": "No autorizado"}), 401

    try:
        if os.path.exists(USUARIOS_FILE):
            os.remove(USUARIOS_FILE)
            return jsonify({"status": "ok", "message": "Archivo usuarios.txt eliminado"})
        else:
            return jsonify({"status": "ok", "message": "El archivo ya no existe"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
