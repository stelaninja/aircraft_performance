from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, FloatField


class AircraftForm(FlaskForm):
    ac_reg = StringField(label="Registration")
    ac_type = StringField(label="Aircraft Type")
    empty_weight = FloatField(label="Empty Weight")
    mtow = FloatField(label="MTOW")
    mlw = FloatField(label="Max Landing Weight")
    max_fuel = FloatField(label="Max Fuel (l)")
    fuel_type = RadioField(label="Fuel Type")
    envelope = StringField(label="Envelope")
    loading_points = StringField(label="Loading Points")
    true_airspeed = FloatField(label="True Airspeed")
    note = StringField(label="Aircraft Notes")
