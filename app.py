# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/")
def home():
    return jsonify({"message": "API Flask corriendo en Render ✅"})

def obtener_ip_publica():
    """Obtiene la IP pública real de la máquina"""
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip = r.json().get("ip")
        return ip
    except Exception:
        return None

@app.route("/mi-ip")
def mi_ip():
    xff = request.headers.get('X-Forwarded-For', '')
    ip = xff.split(',')[0] if xff else request.remote_addr

    if ip.startswith("127.") or ip.startswith("10.") or ip.startswith("192.168."):
        ip_publica = obtener_ip_publica()
        if ip_publica:
            ip = ip_publica

    url = f"http://ip-api.com/json/{ip}?fields=61439"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
