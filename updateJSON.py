#!/usr/bin/python3
# line above allows this file to be directly executable under linux

import json
import pandas as pd
import time
import numpy as np


local = False

if local:
    dataFilePath = "./latest_sint.dat"
    jsonFilePath = "./data.json"
else:
    dataFilePath = "/data/obs/site/cgn/meteo_sinthern/latest_sint.dat"
    jsonFilePath = "/home/citystation/public_html/sintWebDashboard/data.json"
# jsonFilePath = "data.json"


def float_format(x, n_digits):
    # function to format x with n_digits after the decimal point
    # replace decimal point with comma, replace 'nan' with three dashes '---'
    # this works with also with integers or n_digits=0, in contrast to e.g. round( 1.23, 0) which generates '1.0'
    s = (
        ("{0:." + str(n_digits) + "f}")
        .format(x)
        .replace(".", ",")
        .replace("nan", "---")
    )
    return s


def dew_point(T, RH):
    # Function from dx.doi.org/10.1175/BAMS-86-2-225
    # T in Celsius, RH in %
    A = 17.625
    B = 243.04
    frac_1 = B * (np.log(RH / 100) + (A * np.divide(T, np.add(B, T))))
    frac_2 = A - np.log(RH / 100) - A * np.divide(T, np.add(B, T))
    return np.divide(frac_1, frac_2)


# formatting of cloud base heights
def cbh_to_str(cbh_m, cbh_s, n_digits):
    # create string of the form   'mean +/- stddev' (cbh_m+/-cbh_s) with n_digits after the decimal point
    # if  cbh_s == 0  or  cbh_s==nan  only cbh_m is provided, nan is replaced by '---'
    sm = float_format(cbh_m, n_digits)
    ss = float_format(cbh_s, n_digits)

    if (cbh_s == 0) or (sm == "---"):
        s = sm
    else:
        s = sm + "&pm;" + ss
    return s


def updateJSON():
    # read data from files
    df = pd.read_csv(dataFilePath, header=0)

    # convert wind direction
    dir_name = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N",
    ]

    directionLetter = dir_name[int(df["WindDir_D1_WVT"].values.item() / 22.5 + 0.5)]

    # speed in km/h with one digit after the decimal point
    speed = round(float(df["WS_ms_S_WVT"].values.item()) * 3.6, 1)

    # convert utc time stamp into python datetime
    datetime = pd.to_datetime(df["TIMESTAMP"].values.item())

    datetime = datetime.tz_localize("Europe/Berlin")

    df["dewpoint"] = dew_point(df["AirTC_Avg"], df["RH"])
    # create a dict with nicely formatted strings for the variables
    dict = {
        "datetime": datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": {
            "value": round(df["AirTC_Avg"].values.item(), 1),
            "unit": "°C",
            "string": str(round(df["AirTC_Avg"].values.item(), 1)).replace(".", ","),
        },
        "dewpoint": {
            "value": round(df["dewpoint"].values.item(), 1),
            "unit": "°C",
            "string": str(round(df["dewpoint"].values.item(), 1)).replace(".", ","),
        },
        "humidity": {"value": round(df["RH"].values.item(), 0), "unit": "%"},
        "pressure": {
            "value": round(df["BP_mbar_Avg"].values.item(), 0),
            "unit": "hPa",
        },
        "ground-pressure": {
            "value": round(df["BP_mbar_Avg"].values.item(), 0),
            "unit": "hPa",
        },
        "wind_direction": {
            "value": df["WindDir_D1_WVT"].values.item(),
            "unit": "°",
            "string": directionLetter,
        },
        "wind_speed": {
            "value": speed,
            "unit": "km/h",
            "string": str(speed).replace(".", ","),
        },
    }

    # export these strings in data.json
    with open(jsonFilePath, "w") as f:
        json.dump(dict, f)


# run this function twice ...
updateJSON()
time.sleep(30)
updateJSON()
