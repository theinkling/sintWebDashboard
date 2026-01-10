# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from updateJSON import cbh_to_str
import json
import pandas as pd
from updateJSON import dew_point, convert_sea_lvl_pressure


local = False
if local:
    hostName = "localhost"
    serverPort = 8080
    dataFilePath = "./latest_sint.dat"


else:
    hostName = "134.95.211.110"
    serverPort = 5000
    dataFilePath = "/data/obs/site/cgn/meteo_sinthern/latest_sint.dat"
    jsonFilePath = "/home/citystation/public_html/sintWebDashboard/data.json"


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data.json":

            df = pd.read_csv(dataFilePath, header=0)

            datetime = pd.to_datetime(df["TIMESTAMP"].values.item())
            datetime = datetime.tz_localize("utc")

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
            directionLetter = dir_name[int(df["WindDir_D1_WVT"].item() / 22.5 + 0.5)]
            speed = round(df["WS_ms_S_WVT"].item() * 3.6, 1)
            df["dewpoint"] = dew_point(df["AirTC_Avg"], df["RH"])
            dict = {
                "datetime": datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": {
                    "value": round(df["AirTC_Avg"].values.item(), 1),
                    "unit": "°C",
                    "string": str(round(df["AirTC_Avg"].values.item(), 1)).replace(
                        ".", ","
                    ),
                },
                "dewpoint": {
                    "value": round(df["dewpoint"].values.item(), 1),
                    "unit": "°C",
                    "string": str(round(df["dewpoint"].values.item(), 1)).replace(
                        ".", ","
                    ),
                },
                "humidity": {"value": round(df["RH"].values.item(), 0), "unit": "%"},
                "ground-pressure": {
                    "value": round(df["BP_mbar_Avg"].values.item(), 0),
                    "unit": "hPa",
                },
                "pressure": {
                    "value": round(
                        convert_sea_lvl_pressure(
                            df["BP_mbar_Avg"].values.item(),
                            df["AirTC_Avg"].values.item(),
                        ),
                        0,
                    ),
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
            # read last entry from data file and update dict
            # To do
            # serve json
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(dict, ensure_ascii=False), "utf-8"))
        elif self.path == "/script.js":
            # f = open("./index.html")
            self.send_response(200)
            self.send_header("Content-type", "text/javascript")
            self.end_headers()
            # self.wfile.write(bytes(f.read(), 'utf-8'))
            # f.close()
            with open("./script.js", "rb") as file:
                self.wfile.write(file.read())  # Read the file and send the contents
        else:
            # f = open("./index.html")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # self.wfile.write(bytes(f.read(), 'utf-8'))
            # f.close()
            with open("./index.html", "rb") as file:
                self.wfile.write(file.read())  # Read the file and send the contents


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
