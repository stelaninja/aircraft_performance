from geopy.distance import distance


def get_arpt_data(airport):
    fname = f"AIRAC/{airport}.dat"
    arpt_data = {}

    try:
        with open(fname, "r") as f:
            data = f.read().strip().split("\n")
    except (FileNotFoundError, RuntimeError) as err:
        print(f"{err}: Error reading airport file...")
        return None

    for row in data:
        if row.startswith("RWY"):
            row_list = row.split(";")
            rwy = row_list[0][4:8]
            coords = row_list[1].split(",")[:2]
            new_coords = []
            for coord in coords:
                coord = (
                    coord.replace("S", "-")
                    .replace("W", "-")
                    .replace("N", "")
                    .replace("E", "")
                )

                new_coords.append(int(coord) / 1000000)

            arpt_data[rwy] = tuple(new_coords)
    if not arpt_data:
        print(arpt_data)
        return None

    return arpt_data


def dms_to_dd(coords):
    dd = []

    for coord in coords:
        dms = str(coord).split(".")
        d = dms.pop(0)
        m = dms[0][:2]
        s = dms[0][2:4]
        sd = dms[0][4:]

        m = int(m) / 60
        s = int(s) / (60 * 60)

        dd.append(float(d) + float(m) + float(s))

    return tuple(dd)


def get_other_rwy(rwy):
    other_rwy = int(rwy[2:]) + 18
    if other_rwy > 36:
        other_rwy -= 36

    if other_rwy < 10:
        other_rwy = f"0{other_rwy}"

    return f"RW{other_rwy}"


def get_rwy_length(arpt, rwy_sel):
    arpt = arpt.upper()
    rwy_sel = str(rwy_sel).upper()
    arpt_dict = get_arpt_data(arpt)

    if arpt_dict == None:
        print("No runway found")
        return None

    rwys = list(arpt_dict.keys())
    if rwy_sel == "ALL":
        return rwys

    if not rwy_sel.startswith("RW"):
        if len(rwy_sel) == 1:
            rwy_sel = f"RW0{rwy_sel}"
        else:
            rwy_sel = f"RW{rwy_sel}"

    used_rwys = []

    if rwy_sel not in rwys:
        return f"Runway {rwy_sel[2:]} does not exist at {arpt}.\nExisting runways are {*rwys}"
    else:
        for rwy in rwys:
            if rwy in used_rwys:
                continue
            elif rwy == rwy_sel:
                rwy2 = get_other_rwy(rwy)
                coords1 = arpt_dict[rwy]
                coords2 = arpt_dict[rwy2]
                used_rwys.extend([rwy, rwy2])
                rwy_dist = int(distance(dms_to_dd(coords1), dms_to_dd(coords2)).meters)
                return f"RWY {rwy[2:]}-{rwy2[2:]}: {rwy_dist}m"


if __name__ == "__main__":
    print(get_rwy_length("esol", "01"))
