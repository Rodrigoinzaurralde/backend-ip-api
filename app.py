# -*- coding: utf-8 -*-
from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API Flask corriendo en Render ✅"

@app.route("/mi-ip")
def mi_ip():
    url = "http://ip-api.com/json/?fields=61439"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
