import sys
import time
import datetime
import urllib2
import RPi.GPIO as GPIO
from lxml import etree

with open('/home/pi/fmi-apikey.txt', 'r') as f:
    fmi_apikey = f.readline().strip("\n")

upd_interval_min = 15   # FMI data update interval in minutes
query_timestep = 30     # Resolution of the forecast data
endtime = 12            # The amount of hours to show

query_endtime = (datetime.datetime.now().replace(microsecond=0) + 
                 datetime.timedelta(hours = endtime)).isoformat()
query_url = "http://data.fmi.fi/fmi-apikey/{}/wfs?request=getFeature&storedquery_id=fmi::forecast::harmonie::hybrid::point::timevaluepair&latlon=65.01236,25.46816&timestep={}&endtime={}Z".format(fmi_apikey, query_timestep, query_endtime)

current_view = 0
start = time.time()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def get_fmi_data():
    print "{}: Entry" .format(sys._getframe().f_code.co_name)
    
    # Create ElementTree object of the FMI data
    xml_tree = etree.parse(urllib2.urlopen(query_url))
    
    # Get the root element for this tree
    root = xml_tree.getroot()
    
    # Locate time-temperature pairs element
    tnt_elem = root.find(".//*[@gml:id='mts-1-1-Temperature']", root.nsmap)
    
    # Parse time-temperature pairs
    for tvp in tnt_elem.iter(tag="{*}MeasurementTVP"):
        print tvp[0].text, tvp[1].text
    
def change_view(current_view):
    print "{}: Change view: {}-->{}" .format(sys._getframe().f_code.co_name,
        current_view, current_view + 1)
    current_view += 1

GPIO.add_event_detect(7, GPIO.RISING, callback=change_view, bouncetime=300)

# Get data when script is launched
get_fmi_data()
sys.exit()

while True:
    # Do nothing until it's time to update weather data from the server
    # or button is pressed

    # Fetch weather data from the FMI server according to the schedule
    if (time.time() > start + upd_interval_min * 60):
        start = time.time()
        get_fmi_data()

    # Sleep to minimize CPU load
    time.sleep(0.05)
