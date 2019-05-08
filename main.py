import pycom
import time
import _thread
import urequests


from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE



urlDomoticz = "http://192.168.0.17:80/json.htm"

# ------------------------------------------------------------------------------
# sensors data
py = Pysense()
mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
si = SI7006A20(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)


# ------------------------------------------------------------------------------
# Do we need to turn on the light or not ?
light = lt.light()
lightResult = (int(light[0]) + int(light[1])) / 2
if( lightResult <= 300 ):
    booLight = False
else:
    booLight = True



def sendTemperatur():
    pybytes.send_signal(1, si.temperature())
    pybytes.send_signal(2, si.humidity())
    pybytes.send_signal(3, si.dew_point())




def sendLight():
    light = lt.light()
    lightResult = (int(light[0]) + int(light[1])) / 2
    pybytes.send_signal(4, lightResult)
    Requete = urequests.get(urlDomoticz, { "type":"command",
                                            "param":"udevice",
                                            "idx":276,
                                            "svalue":lightResult} )




def sendAltitude():
    mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
    pression = mpp.pressure()
    pybytes.send_signal(5, mp.altitude())
    pybytes.send_signal(6, pression)
    Requete = urequests.get(urlDomoticz, { "type":"command",
                                            "param":"udevice",
                                            "idx":278,
                                            "svalue":pression} )




def sendBatteryVoltage():
    battery = py.read_battery_voltage()
    pybytes.send_signal(7, battery)
    Requete = urequests.get(urlDomoticz,{ "type":"command",
                                        "param":"udevice",
                                        "idx":277,
                                        "svalue":battery} )




def mainTread():
    # send mesures
    pycom.heartbeat(False)
    if( booLight ):
        pycom.rgbled(0x550000)
    sendLight()
    sendTemperatur()
    sendBatteryVoltage()
    sendAltitude()

    # Blink in green to indicate that mesures have be send
    if( booLight ):
        pycom.rgbled(0x005500)
        time.sleep(1)

    # If we have been waked up by movement
    # we are waiting for 1 minute. This is suppose to be a safe mode to allow
    # transfers
    if( py.get_wake_reason() != 4):
        print("Waiting for human control during 30 seconds")
        print("Last wakeup reason: " + str(py.get_wake_reason()) + "; Aproximate sleep remaining: " + str(py.get_sleep_remaining()) + " sec")
        pycom.heartbeat(True)
        time.sleep(30)


    # indicate that we are going to deep sleep
    if( booLight ):
        pycom.heartbeat(False)
        pycom.rgbled(0xFFFFFF)
        time.sleep(0.1)
        pycom.rgbled(0xDDDDDD)
        time.sleep(0.2)
        pycom.rgbled(0xBBBBBB)
        time.sleep(0.2)
        pycom.rgbled(0x999999)
        time.sleep(0.2)
        pycom.rgbled(0x777777)
        time.sleep(0.2)
        pycom.rgbled(0x555555)
        time.sleep(0.2)
        pycom.rgbled(0x333333)
        time.sleep(0.2)
        pycom.rgbled(0x111111)
        time.sleep(0.2)

    # going to sleep
    py.go_to_sleep()




# ==============================================================================
# settings deep sleep mode
py.setup_int_pin_wake_up(True)
py.setup_int_wake_up(True, True)
py.setup_sleep(60 * 30) # deep sleep for 2 minutes

# enable sensor to wake up
acc = LIS2HH12()
acc.enable_activity_interrupt(500, 200)


# Send data and go to deep sleep
_thread.start_new_thread(mainTread, ())
