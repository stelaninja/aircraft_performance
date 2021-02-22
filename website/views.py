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
    load_scheme = ast.literal_eval(request.args.get("load_scheme"))
    fuel = float(request.args.get("fuel"))
    fuel_burn = float(request.args.get("fuel_burn"))
    print("LOAD SCHEME FOR PLOT IS TYPE:", type(load_scheme))
    print(load_scheme)
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
        weights=load_scheme, fuel_ltr=fuel, fuel_burn=fuel_burn,
    )

    wandb.print_data(ac_model)

    # save the fig to the image

    fig = wandb.plot_envelope(ac_model)
    plt.text(90, 900, "TEST")
    # create canvas and image
    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype="img/png", cache_timeout=0)


@views.route("/calculate", methods=["GET", "POST"])
@login_required
def calculate():
    load_scheme = {}
    if request.method == "POST":
        ac_id = request.form.get("ac_id")
        fuel = request.form.get("fuel")
        fuel_burn = request.form.get("fuel_burn")

        print("LOAD SCHEME")
        form_data = request.form
        for key in form_data.keys():
            for value in form_data.getlist(key):
                if key not in ["ac_id", "fuel", "fuel_burn"]:
                    if value == "":
                        value = 0
                    load_scheme[key] = float(value)
                print(key, ":", value)
    else:
        ac_id = request.args.get("ac_id")
    aircraft = Aircraft.query.filter_by(id=ac_id).first()

    return render_template(
        "calculate.html",
        aircraft=aircraft,
        user=current_user,
        load_scheme=load_scheme,
        fuel=fuel,
        fuel_burn=fuel_burn,
    )


@views.route("/load-aircraft")
@login_required
def load_aircraft():
    ac_id = request.args.get("ac_id")
    aircraft = Aircraft.query.filter_by(id=ac_id).first()
    loading_points = ast.literal_eval(aircraft.loading_points)

    return render_template(
        "load-aircraft.html",
        aircraft=aircraft,
        loading_points=loading_points,
        user=current_user,
    )


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
