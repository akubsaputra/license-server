from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models import db, User
from flask_bcrypt import Bcrypt
from datetime import datetime

admin = Blueprint("admin", __name__)
bcrypt = Bcrypt()

ADMIN_USERNAME = "admin"       # change via env/system later if needed
ADMIN_PASSWORD = "supersecret" # change via env/system later if needed

@admin.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USERNAME and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin.dashboard"))
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)

@admin.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin.admin_login"))

@admin.route("/admin/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("dashboard.html", users=users)

@admin.route("/admin/add", methods=["POST"])
def add_user():
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    username = request.form.get("username")
    password = request.form.get("password")
    expires = request.form.get("expires") or None
    max_devices = int(request.form.get("max_devices") or 1)

    if not username or not password:
        return redirect(url_for("admin.dashboard"))

    # prevent duplicates
    if User.query.filter_by(username=username).first():
        return redirect(url_for("admin.dashboard"))

    exp_date = None
    if expires:
        try:
            exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
        except Exception:
            exp_date = None

    user = User(
        username=username,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        expires=exp_date,
        max_devices=max_devices
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))

@admin.route("/admin/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))
