from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Aircraft
from . import db
import json


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        ac_reg = request.form.get("ac_reg")
        ac_type = request.form.get("ac_type")
        empty_weight = request.form.get("empty_weight").replace(",", ".")
        # empty_weight = request.form.get("empty_weight")
        # mtow = request.form.get("mtow")
        mtow = request.form.get("mtow").replace(",", ".")
        true_airspeed = request.form.get("true_airspeed")
        note = request.form.get("note")

        if len(ac_reg) < 3:
            flash("Aircraft registration is to short.", category="error")
        else:
            new_aircraft = Aircraft(
                registration=ac_reg,
                aircraft_type=ac_type,
                empty_weight=empty_weight,
                mtow=mtow,
                true_airspeed=true_airspeed,
                data=note,
                user_id=current_user.id,
            )
            db.session.add(new_aircraft)
            db.session.commit()
            flash("Aircraft added!", category="success")

    return render_template("home.html", user=current_user)


@views.route("/edit-aircraft", methods=["GET", "POST"])
def edit_aircraft():
    if request.method == "POST":
        ac_id = request.form.get("ac_id")
        aircraft = Aircraft.query.filter_by(id=ac_id).first()

    return render_template("edit_aircraft.html", aircraft=aircraft, user=current_user)


@views.route("/update-aircraft", methods=["POST"])
def update_aircraft():
    print("CORRECT")
    ac_id = request.form.get("ac_id")
    ac_reg = request.form.get("ac_reg")
    ac_type = request.form.get("ac_type")
    empty_weight = request.form.get("empty_weight").replace(",", ".")
    mtow = request.form.get("mtow").replace(",", ".")
    true_airspeed = request.form.get("true_airspeed")
    note = request.form.get("note")

    if len(ac_reg) < 3:
        flash("Aircraft registration is to short.", category="error")
    else:
        aircraft = db.session.query(Aircraft).filter(Aircraft.id == ac_id).one()
        aircraft.registration = ac_reg
        aircraft.aircraft_type = ac_type
        aircraft.empty_weight = empty_weight
        aircraft.mtow = mtow
        aircraft.true_airspeed = true_airspeed
        aircraft.data = note

        db.session.commit()
        flash("Aircraft updated!", category="success")

        aircraft = Aircraft.query.filter_by(id=ac_id).first()

    return render_template("edit_aircraft.html", aircraft=aircraft, user=current_user)


@views.route("/delete-aircraft", methods=["POST"])
def delete_aircraft():
    aircraft = json.loads(request.data)
    aircraftId = aircraft["aircraftId"]
    aircraft = Aircraft.query.get(aircraftId)
    if aircraft:
        if aircraft.user_id == current_user.id:
            db.session.delete(aircraft)
            db.session.commit()

    return jsonify({})
