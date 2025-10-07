from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models import db, User, Device
from flask_bcrypt import Bcrypt
import hashlib

api = Blueprint("api", __name__)
bcrypt = Bcrypt()

def hash_device(device_info: str) -> str:
    return hashlib.sha256((device_info or "").encode("utf-8")).hexdigest()

@api.route("/health")
def health():
    return jsonify({"status": "ok"})

@api.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    device = data.get("device", "")

    if not username or not password:
        return jsonify({"status": "error", "message": "username/password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"status": "error", "message": "user not found"}), 404

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"status": "error", "message": "invalid credentials"}), 401

    # Check expiry
    if user.expires and datetime.utcnow().date() > user.expires:
        return jsonify({"status": "error", "message": "license expired"}), 403

    # Check devices
    device_id = hash_device(device)
    existing = Device.query.filter_by(device_hash=device_id, user_id=user.id).first()
    if existing:
        return jsonify({"status": "ok", "message": "login successful"})
    else:
        if len(user.devices) < user.max_devices:
            new_device = Device(device_hash=device_id, user_id=user.id)
            db.session.add(new_device)
            db.session.commit()
            return jsonify({"status": "ok", "message": "device registered"})
        else:
            return jsonify({"status": "error", "message": "device limit reached", "max_devices": user.max_devices}), 403
