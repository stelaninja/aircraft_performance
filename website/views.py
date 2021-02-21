from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    jsonify,
    send_file,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
from .models import Aircraft
from .forms import AircraftForm
from . import w_and_b as wandb
from . import db
import json, io, ast
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    form = AircraftForm()

    return render_template("home.html", user=current_user, form=form)


@views.route("/plot")
def plot():
    ac_id = request.args.get("ac_id")
    aircraft = Aircraft.query.filter_by(id=ac_id).first()
    print("AIRCRAFT ID:", ac_id)
    print(list(ast.literal_eval(aircraft.envelope)))
    ac_model = wandb.AircraftModel(
        ac_reg=aircraft.registration,
        type=aircraft.aircraft_type,
        mtow=aircraft.mtow,
        mlw=aircraft.mlw,
        empty_weight=aircraft.empty_weight,
        max_fuel=aircraft.max_fuel,
        fuel_type=aircraft.fuel_type,
        envelope=list(ast.literal_eval(aircraft.envelope)),
        loading_points=ast.literal_eval(aircraft.loading_points),
    )

    ac_model.load_aircraft(
        weights={
            "pilot": 90,
            "front_pax": 80,
            "rear_pax1": 0,
            "rear_pax2": 0,
            "std_bagg": 10,
            "fwd_ext_bagg": 0,
            "aft_ext_bagg": 0,
        },
        fuel_ltr=100,
        fuel_burn=50,
    )

    wandb.print_data(ac_model)

    # save the fig to the image

    fig = wandb.plot_envelope(ac_model)
    # create canvas and image
    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype="img/png", cache_timeout=0)


@views.route("/calculate")
def calculate():
    ac_id = request.args.get("ac_id")
    aircraft = Aircraft.query.filter_by(id=ac_id).first()

    return render_template("calculate.html", aircraft=aircraft, user=current_user)


@views.route("/load-aircraft")
def load_aircraft():
    ac_id = request.args.get("ac_id")
    aircraft = Aircraft.query.filter_by(id=ac_id).first()

    return render_template("load-aicraft.html", aircraft=aircraft)


@views.route("/edit-aircraft", methods=["GET", "POST"])
@login_required
def edit_aircraft():
    if request.method == "POST":
        ac_id = request.form.get("ac_id")
        aircraft = Aircraft.query.filter_by(id=ac_id).first()

    form = AircraftForm()

    return render_template(
        "edit_aircraft.html", aircraft=aircraft, form=form, user=current_user
    )


@views.route("/update-aircraft", methods=["POST"])
@login_required
def update_aircraft():
    ac_id = request.form.get("ac_id")
    ac_reg = request.form.get("ac_reg")
    ac_type = request.form.get("ac_type")
    empty_weight = request.form.get("empty_weight").replace(",", ".")
    mtow = request.form.get("mtow").replace(",", ".")
    mlw = request.form.get("mlw").replace(",", ".")
    max_fuel = request.form.get("max_fuel")
    fuel_type = request.form.get("fuel_type")
    envelope = request.form.get("envelope")
    loading_points = request.form.get("loading_points")
    true_airspeed = request.form.get("true_airspeed")
    note = request.form.get("note")

    print(ac_reg, fuel_type)
    if len(ac_reg) < 3:
        flash("Aircraft registration is to short.", category="error")
    else:
        aircraft = db.session.query(Aircraft).filter(Aircraft.id == ac_id).one()
        aircraft.registration = ac_reg
        aircraft.aircraft_type = ac_type
        aircraft.empty_weight = empty_weight
        aircraft.mtow = mtow
        aircraft.mlw = mlw
        aircraft.max_fuel = max_fuel
        aircraft.fuel_type = fuel_type
        aircraft.envelope = envelope
        aircraft.loading_points = loading_points
        aircraft.true_airspeed = true_airspeed
        aircraft.data = note

        db.session.commit()
        flash("Aircraft updated!", category="success")

        aircraft = Aircraft.query.filter_by(id=ac_id).first()
        form = AircraftForm()

    return render_template(
        "edit_aircraft.html", aircraft=aircraft, form=form, user=current_user
    )


@views.route("/add-aircraft", methods=["GET", "POST"])
@login_required
def add_aircraft():
    if request.method == "POST":
        ac_reg = request.form.get("ac_reg")
        ac_type = request.form.get("ac_type")
        empty_weight = request.form.get("empty_weight").replace(",", ".")
        mtow = request.form.get("mtow").replace(",", ".")
        mlw = request.form.get("mlw").replace(",", ".")
        max_fuel = request.form.get("max_fuel")
        fuel_type = request.form.get("fuel_type")
        envelope = request.form.get("envelope")
        loading_points = request.form.get("loading_points")
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
                mlw=mlw,
                max_fuel=max_fuel,
                fuel_type=fuel_type,
                envelope=envelope,
                loading_points=loading_points,
                true_airspeed=true_airspeed,
                data=note,
                user_id=current_user.id,
            )

            print(fuel_type)
            db.session.add(new_aircraft)
            db.session.commit()
            flash("Aircraft added!", category="success")

        return redirect(url_for("views.home"))
    form = AircraftForm()
    return render_template("add_aircraft.html", form=form, user=current_user)


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
