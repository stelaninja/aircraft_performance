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
from .models import Aircraft, User
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
    aircrafts = Aircraft.query.order_by(Aircraft.id).all()

    return render_template(
        "home.html", aircrafts=aircrafts, user=current_user, form=form,
    )


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
    load_scheme2 = load_scheme.copy()
    for key in ["ac_id", "fuel", "fuel_burn"]:
        del load_scheme2[key]
    ac_model.load_aircraft(
        weights=load_scheme2, fuel_ltr=fuel, fuel_burn=fuel_burn,
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
        will_plot = True

        print("LOAD SCHEME")
        form_data = request.form
        for key in form_data.keys():
            for value in form_data.getlist(key):
                # if key not in ["ac_id", "fuel", "fuel_burn"]:
                if value == "":
                    value = 0
                load_scheme[key] = float(value)
                print(key, ":", value)
    else:
        ac_id = request.args.get("ac_id")
        will_plot = False

    aircraft = Aircraft.query.filter_by(id=ac_id).first()
    loading_points = ast.literal_eval(aircraft.loading_points)

    return render_template(
        "load-aircraft.html",
        aircraft=aircraft,
        user=current_user,
        load_scheme=load_scheme,
        loading_points=loading_points,
        fuel=fuel,
        fuel_burn=fuel_burn,
        will_plot=will_plot,
    )


@views.route("/load-aircraft")
@login_required
def load_aircraft():
    ac_id = request.args.get("ac_id")
    aircraft = Aircraft.query.filter_by(id=ac_id).first()
    loading_points = ast.literal_eval(aircraft.loading_points)
    load_scheme = {}

    return render_template(
        "load-aircraft.html",
        aircraft=aircraft,
        loading_points=loading_points,
        user=current_user,
        load_scheme=load_scheme,
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

    owned_aircrafts = [x.id for x in current_user.aircrafts]

    if int(ac_id) not in owned_aircrafts:
        flash(
            "You do not own this aircraft and is not allowed to update.",
            category="error",
        )
        aircraft = None
    elif len(ac_reg) < 3:
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


@views.route("/aircraft-data/<ID>")
def aircraft_data(ID):
    aircraft = Aircraft.query.filter_by(id=ID).first()
    aircraft_dict = {}

    aircraft_dict["loading_points"] = ast.literal_eval(aircraft.loading_points)
    response = jsonify({"aircraft": aircraft_dict})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response

@views.route("/delete-aircraft", methods=["POST"])
@login_required
def delete_aircraft():
    aircraft = json.loads(request.data)
    aircraftId = aircraft["aircraftId"]
    aircraft = Aircraft.query.get(aircraftId)
    if aircraft:
        if aircraft.user_id == current_user.id or current_user.id == 1:
            db.session.delete(aircraft)
            db.session.commit()

    return jsonify({})

@views.route("/delete-user", methods=["POST"])
@login_required
def delete_user():

    user = json.loads(request.data)
    userId = user["userId"]
    user_to_delete = User.query.get(userId)
    print(user_to_delete)
    if user_to_delete:
        if user_to_delete.id == current_user.id:
            flash("You cannot delete your self at this moment!", category="error")
        else:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash(f"User {user_to_delete.id} is removed", category="success")

    return jsonify({})


@login_required
@views.route("/users")
def users():
    all_users = User.query.order_by(User.id).all()

    return render_template("users.html", user=current_user, all_users=all_users)
