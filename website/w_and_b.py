import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from flask import send_file
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from shapely.geometry import Point, Polygon


class AircraftModel:
    def __init__(
        self,
        ac_reg,
        type,
        mtow,
        mlw,
        empty_weight,
        max_fuel,
        fuel_type,
        envelope=[(0, 0), (0, 0), (0, 0), (0, 0)],
        loading_points={},
    ):
        self.ac_reg = ac_reg
        self.type = type
        self.mtow = mtow
        self.mlw = mlw
        self.empty_weight = empty_weight
        self.max_fuel = max_fuel
        self.fuel_type = fuel_type  # 0 for Jet A1, 1 for Avgas
        self.envelope = envelope
        self.loading_points = loading_points
        self.fuel_weight = 0

        if self.fuel_type == 0 or self.fuel_type == "jet":
            self.fuelcoeff = 0.8
        else:
            self.fuelcoeff = 0.72

    def trip(self, kg_fuel_burn):
        # calculate fuel weight at end of flight
        self.fuel_weight = self.fuel_weight - kg_fuel_burn
        if self.fuel_weight < 0:
            self.fuel_weight = 0

        # remaining fuel afer flight
        self.remaining_fuel = self.fuel_weight / self.fuelcoeff

        # calculate landing weight
        self.LAW = self.TOW - kg_fuel_burn

    def load_aircraft(self, weights={}, fuel_ltr=148, fuel_burn=0):
        self.EFW = self.empty_weight
        self.fuel_weight = fuel_ltr * self.fuelcoeff
        self.fuel_ltr = fuel_ltr
        fuel_burn = fuel_burn * self.fuelcoeff

        # add payload
        for weight in weights:
            self.EFW += weights[weight]

        self.TOW = self.MFW = self.EFW

        # add fuel weights
        self.TOW += fuel_ltr * self.fuelcoeff
        self.MFW += self.max_fuel * self.fuelcoeff

        # calculate min and max CGs
        cgs = [x for x, y in self.envelope]
        self.min_cg = min(cgs)
        self.max_cg = max(cgs)

        # calculate acutal CGs
        MM = self.empty_weight * self.loading_points["empty_weight"]
        MM_fuel = self.fuel_weight * self.loading_points["fuel"]
        for lp in weights:
            MM += weights[lp] * self.loading_points[lp]

        self.CG_takeoff = round((MM + MM_fuel) / self.TOW, 2)

        self.trip(fuel_burn)

        self.CG_land = round(
            (MM + ((self.fuel_weight) * self.loading_points["fuel"])) / self.LAW, 2
        )

        self.CG_maxfuel = round(
            (MM + ((self.max_fuel * self.fuelcoeff) * self.loading_points["fuel"]))
            / self.MFW,
            2,
        )

        self.CG_emptyfuel = round(MM / self.EFW, 2)


# PLOT ENVELOPE
def plot_envelope(aircraft):
    plt.switch_backend("Agg")
    sns.set_style("whitegrid")

    # create envelope polygon
    codes = (
        [Path.MOVETO] + [Path.LINETO] * (len(aircraft.envelope) - 1) + [Path.CLOSEPOLY]
    )
    vertices = aircraft.envelope + [(0, 0)]
    path = Path(vertices, codes)
    pathpatch = PathPatch(path, facecolor="None", edgecolor="darkgrey", linewidth=4)

    # create figure and subplot
    fig, ax = plt.subplots(figsize=(12, 12))

    # plot CG change from takeoff to landing
    sc = sns.scatterplot(
        ax=ax,
        x=[aircraft.CG_takeoff, aircraft.CG_land],
        y=[aircraft.TOW, aircraft.LAW],
        marker="X",
        linewidth=0,
        s=50,
        color="black",
        zorder=2,
    )

    # Fix the markers
    if 0.5 < aircraft.remaining_fuel / aircraft.max_fuel < 0.75:
        fuel_marker = "bottom"
    elif (aircraft.remaining_fuel / aircraft.max_fuel) < 0.5:
        fuel_marker = "none"
    else:
        fuel_marker = "full"

    sc.cla()
    markers = ["X", "h", "o", "o"]
    sizes = [10, 10, 10, 10]
    facecolors = ["tab:blue", "tab:blue", "tab:green", "tab:red"]
    altcolors = ["lightgrey", "lightsteelblue", "lightsteelblue", "tab:red"]
    fillstyles = ["full", str(fuel_marker), "full", "none"]
    orders = [3, 2, 0, 1]
    for i, mark in enumerate(
        [
            (aircraft.CG_takeoff, aircraft.TOW),
            (aircraft.CG_land, aircraft.LAW),
            (aircraft.CG_maxfuel, aircraft.MFW),
            (aircraft.CG_emptyfuel, aircraft.EFW),
        ]
    ):
        sc.plot(
            mark[0],
            mark[1],
            markersize=sizes[i],
            marker=markers[i],
            markerfacecolor=facecolors[i],
            markerfacecoloralt=altcolors[i],
            markeredgewidth=0.3,
            markeredgecolor="black",
            fillstyle=fillstyles[i],
            zorder=2 + orders[i],
        )

    # plot CG change from max fuel to empty fuel
    lp = sns.lineplot(
        ax=ax,
        x=[aircraft.CG_maxfuel, aircraft.CG_emptyfuel],
        y=[aircraft.MFW, aircraft.EFW],
        linewidth=3,
        color="orange",
        zorder=1,
    )

    # plot the envelope polygon
    ax.add_patch(pathpatch)

    # Check if CGs are within envelope
    cg_to = Point(aircraft.CG_takeoff, aircraft.TOW)
    cg_l = Point(aircraft.CG_land, aircraft.LAW)

    # Create a Polygon
    poly = Polygon(aircraft.envelope)

    # show warning if outside envelope
    text_str = []

    if not cg_to.within(poly) or not cg_l.within(poly):
        cg_outside_limit = True
        text_str.append("Aircraft CG outside envelope limits")
    else:
        cg_outside_limit = False
    if aircraft.LAW > aircraft.mlw:
        exceed_land_weight = True
        text_str.append("Max landing weight exceeded")
    else:
        exceed_land_weight = False
    if aircraft.TOW > aircraft.mtow:
        overweight = True
        text_str.append("Aircraft is overloaded")
    else:
        overweight = False

    # if not cg_to.within(poly) or not cg_l.within(poly) or aircraft.LAW > aircraft.mlw:
    if exceed_land_weight or cg_outside_limit or overweight:

        textstr = "\n".join(text_str).upper() + "\n\nTAKE OFF NOT ALLOWED"

        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle="round", facecolor="red", alpha=0.5)

        # place a text box in upper left in axes coords
        ax.text(
            0.5,
            0.5,
            textstr,
            transform=ax.transAxes,
            fontsize=24,
            fontweight="bold",
            verticalalignment="top",
            horizontalalignment="center",
            bbox=props,
        )

    ax.set_title("Weight and Balance", size=16)

    # adjust the plot to give space for text box
    plt.subplots_adjust(bottom=0.5)

    # add text box
    text_str = "\n".join(print_data(aircraft))
    props = dict(boxstyle="round", facecolor="blue", alpha=0.5)
    plt.text(
        0.5,
        -0.1,
        text_str,
        transform=ax.transAxes,
        fontsize=14,
        verticalalignment="top",
        horizontalalignment="center",
        bbox=props,
    )

    plt.xlim(aircraft.min_cg - 0.5, aircraft.max_cg + 0.5)
    plt.ylim(aircraft.empty_weight - 20, aircraft.mtow + 20)

    plt.suptitle(
        f"{aircraft.ac_reg} ({aircraft.type})", size=20, fontweight="bold", y=0.95
    )

    # plt.show()
    return fig


def print_data(aircraft):
    bold_div = "=" * 10
    divider = "-" * 20
    title_str = f"{bold_div} AIRCRAFT -- {aircraft.type} {bold_div}"
    bold_div_len = int((len(title_str) / 2) - (len(aircraft.ac_reg) / 2))

    info_text = []

    info_text.append("Weights (kg)")
    info_text.append(divider)
    info_text.append(
        f"Empty Weight: {aircraft.empty_weight:.2f}\nTOW: {aircraft.TOW:.2f}\nLAW: {aircraft.LAW:.2f}\nMFW: {aircraft.MFW:.2f}\nEFW: {aircraft.EFW:.2f}"
    )
    info_text.append("\nFuel")
    info_text.append(divider)
    info_text.append(
        f"Fuel weight (Take off): {aircraft.fuel_weight + aircraft.TOW - aircraft.LAW:.2f} kg"
    )
    info_text.append(f"Fuel weight (Landing): {aircraft.fuel_weight:.2f} kg")
    info_text.append(f"Fuel burn: {aircraft.TOW - aircraft.LAW:.2f} kg")
    info_text.append(
        f"Fuel remaining: {aircraft.remaining_fuel:.2f} / {aircraft.max_fuel:.2f} ({round((aircraft.remaining_fuel / aircraft.max_fuel) * 100, 2)}%)"
    )
    info_text.append("\nBalance")
    info_text.append(divider)
    info_text.append(
        f"CG at takeoff: {aircraft.CG_takeoff:.2f}\nCG at landing: {aircraft.CG_land:.2f}"
    )

    # print(title_str)
    # print(f"{bold_div:{bold_div_len}}{aircraft.ac_reg}{bold_div:>{bold_div_len}}")

    # print("Weights (kg)")
    # print(divider)
    # print(f"Empty Weight: {aircraft.empty_weight:.2f}")
    # print(f"TOW: {aircraft.TOW:.2f}\nLAW: {aircraft.LAW:.2f}")
    # print(f"MFW: {aircraft.MFW:.2f}\nEFW: {aircraft.EFW:.2f}")

    # print("\nFuel")
    # print(divider)
    # print(
    #     f"Fuel remaining: {aircraft.remaining_fuel:.2f} / {aircraft.max_fuel:.2f} ({round((aircraft.remaining_fuel / aircraft.max_fuel) * 100, 2)}%)"
    # )
    # print(
    #     f"Fuel weight (Take off): {aircraft.fuel_weight + aircraft.TOW - aircraft.LAW:.2f} kg"
    # )
    # print(f"Fuel weight (Landing): {aircraft.fuel_weight:.2f} kg")
    # print(f"Fuel burn: {aircraft.TOW - aircraft.LAW:.2f} kg")

    # print("\nBalance")
    # print(divider)
    # print(
    #     f"CG at takeoff: {aircraft.CG_takeoff:.2f}\nCG at landing: {aircraft.CG_land:.2f}"
    # )

    return info_text


if __name__ == "__main__":
    ln_ftm = AircraftModel(
        ac_reg="LN-FTM",
        type="DA40NG",
        mtow=1310,
        mlw=1280,
        empty_weight=933.4,
        max_fuel=148,
        fuel_type=0,
        envelope=[(94.5, 940), (94.5, 1080), (97.2, 1310), (99.6, 1310), (99.6, 940)],
        loading_points={
            "empty_weight": 96.26,
            "pilot": 90.60,
            "front_pax": 90.60,
            "rear_pax1": 128.0,
            "rear_pax2": 128.0,
            "std_bagg": 143.7,
            "fwd_ext_bagg": 153.15,
            "aft_ext_bagg": 178.74,
            "fuel": 103.50,
        },
    )

    ln_ftm.load_aircraft(
        weights={
            "pilot": 90,
            "front_pax": 0,
            "rear_pax1": 70,
            "rear_pax2": 25,
            "std_bagg": 5,
            "fwd_ext_bagg": 5,
            "aft_ext_bagg": 5,
        },
        fuel_ltr=148,
        fuel_burn=120,
    )

    print_data(ln_ftm)
    plot_envelope(ln_ftm)
