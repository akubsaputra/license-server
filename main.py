from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ Indotex License Server aktif di Railway!'

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Jangan jalankan app.run() langsung kecuali ini main module
if __name__ == "__main__":
    # Railway kasih port lewat environment variable "PORT"
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
