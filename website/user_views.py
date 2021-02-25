from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

user_views = Blueprint("user_views", __name__)


@login_required
@user_views.route("/profile")
def profile():
    return render_template("profile.html", user=current_user)


@user_views.route("/update-user", methods=["POST"])
@login_required
def update_user():
    user_id = request.form.get("user_id")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    if len(email) < 5:
        flash("Not a valid e-mail.", category="error")

    elif password1 != password2:
        flash("Passwords don't match.", category="error")

    elif 0 < len(password1) < 6:
        flash("Password must be at least 6 characters.", category="error")

    else:
        user = db.session.query(User).filter(User.id == user_id).one()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        if len(password1) > 0:
            user.password = generate_password_hash(password1, method="sha256")

        db.session.commit()
        flash("User updated!", category="success")

    return render_template("profile.html", user=current_user)

