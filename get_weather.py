try:
    import os
    import sys
    import time
    import datetime
    import dateutil.parser
    import urllib.request
    import random
    import RPi.GPIO as GPIO
    import pytz
    import json
    from subprocess import call, check_output
    from lxml import etree

    with open('/home/pi/fmi-apikey.txt', 'r') as f:
        fmi_apikey = f.readline().strip("\n")

    json_db_file = "/var/www/taikapeili/weather_data.json"
    upd_interval_min = 15   # FMI data update interval in minutes
    q_timestep = 60         # Resolution of the forecast data
    endtime = 24            # The amount of hours to show
    n_of_data_points = endtime * (q_timestep / 60) + 2
    current_view = 0
    button_pressed = False
    retry_interval = 20
    retry_count = 3
    button_pin = 11
    # TODO: Calculate based on sunrise/sunset
    night_hours = [19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
    d_name_map = {"Mon": ("Ma", "Maanantai"),
                  "Tue": ("Ti", "Tiistai"),
                  "Wed": ("Ke", "Keskiviikko"),
                  "Thu": ("To", "Torstai"),
                  "Fri": ("Pe", "Perjantai"),
                  "Sat": ("La", "Lauantai"),
                  "Sun": ("Su", "Sunnuntai")}

    start = time.time()

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

except Exception as e:
    _print_debug("Failed to setup: {}".format(e))
    sys.exit()

def _print_debug(string):
    string = "[" + str(datetime.datetime.now()) + "] " + string
    print(string)
    with open("/var/www/taikapeili/debug.log", "a") as dfile:
        dfile.write(string + "\n")

def get_fmi_data():

    weather_params_list = []

    q_endtime = (datetime.datetime.now().replace(microsecond=0) + 
                     datetime.timedelta(hours = endtime)).isoformat()
    q_storedquery_id = "fmi::forecast::hirlam::surface::point::timevaluepair"
    q_latlon = "65.01236,25.46816"
    q_parameters = "Temperature,WeatherSymbol3"
    query_url = "http://data.fmi.fi/fmi-apikey/{}/wfs?request=getFeature&" \
                "storedquery_id={}&" \
                "latlon={}&" \
                "timestep={}&" \
                "parameters={}&" \
                "endtime={}Z" \
                .format(fmi_apikey, q_storedquery_id, q_latlon, q_timestep,
                        q_parameters, q_endtime)
    _print_debug("Query to send: {}".format(query_url))

    # Fetch FMI data - retry if fails
    for r in range(retry_count):
        try:
            # Create ElementTree object of the FMI data
            xml_tree = etree.parse(urllib.request.urlopen(query_url))
            break
        except Exception as e:
            _print_debug("Error fetching FMI data: '{}'. Retry {}/{} in {} s "
                         .format(e, r + 1, retry_count, retry_interval))
            time.sleep(retry_interval)

    # Get the root element for this tree
    root = xml_tree.getroot()

    # Locate time-temperature pairs element
    tnt_elem = root.find(".//*[@gml:id='mts-1-1-Temperature']", root.nsmap)

    # Parse time - temperature pairs
    for tvp in tnt_elem.iter(tag="{*}MeasurementTVP"):
        d_and_t = dateutil.parser.parse(tvp[0].text).astimezone(pytz.timezone("Europe/Helsinki"))
        d_name = dateutil.parser.parse(tvp[0].text).astimezone(pytz.timezone("Europe/Helsinki")).strftime("%a")
        d = d_and_t.strftime("%d.%m.")
        if int(d_and_t.strftime("%H")) in night_hours:
            night = True
        else:
            night = False
        t = d_and_t.strftime("%H:%M")
        temp = round(float(tvp[1].text))
        weather_params_list.append({"date": d, "time": t,
                                    "temperature": temp, "night": night,
                                    "weekday_short": d_name_map[d_name][0],
                                    "weekday": d_name_map[d_name][1]})

    # Locate time - weather symbol pairs element
    ws_elem = root.find(".//*[@gml:id='mts-1-1-WeatherSymbol3']", root.nsmap)

    # Parse weather symbols from the XML elements
    for n, twsp in enumerate(ws_elem.iter(tag="{*}MeasurementTVP")):
        wsymbol = int(float(twsp[1].text))
        weather_params_list[n]["wsymbol"] = wsymbol
        if n < (n_of_data_points / 2):
            weather_params_list[n]["column"] = "left"
        else:
            weather_params_list[n]["column"] = "right"

    # Collect JSON metadata and add to the JSON structure
    meta = {"updated": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
    weather_params_list.append(meta)

    with open(json_db_file, "w") as f:
        json.dump(weather_params_list, f, indent=4)
        _print_debug("Weather data written to {}".format(json_db_file))

def change_view(view_now):
    if view_now == 2:
        view_now = 0
    else:
        view_now += 1
    _print_debug("Change view to {}" .format(view_now))
    x = int(view_now) * 5 + 2
    
    xdo_move_cmd = "xdotool search --class kweb3 mousemove --sync " + str(x) + " " + str(2)
    xdo_click_cmd = "xdotool search --class kweb3 click 1"

    try:
        call(xdo_move_cmd.split())
        call(xdo_click_cmd.split())
    except Exception as e:
        _print_debug("xdotool failed! \n{}".format(e))
        sys.exit()

    return view_now

# Get data when script is launched
try:
    get_fmi_data()
    # Set display to path
    os.environ["DISPLAY"] = ":0.0"
except Exception as e:
    _print_debug("Failure in startup: {}".format(e))
    sys.exit()

prev_input = 0
while True:
    try:
        # Do nothing until it's time to update weather data from the server
        # or button is pressed
        input = GPIO.input(button_pin)
        if ((not prev_input) and input):
            # Prevent short voltage drops from being interpreted as button presses
            time.sleep(0.05)
            if GPIO.input(button_pin):
                current_view = change_view(current_view)
            time.sleep(0.3)
        prev_input = input

        # Fetch weather data from the FMI server according to the schedule
        if (time.time() > start + upd_interval_min * 60):
            start = time.time()

            # TODO: thread me!
            get_fmi_data()

        # Sleep to minimize CPU load
        time.sleep(0.05)

    except Exception as e:
        _print_debug("Failure in main loop: {}".format(e))
