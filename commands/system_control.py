import os
import ctypes
import psutil

def shutdown():
    os.system("shutdown /s /t 1")
    return "Shutting down the system."

def restart():
    os.system("shutdown /r /t 1")
    return "Restarting the system."

def set_volume(level):
    return "Volume adjustment not implemented yet."

def set_brightness(level):
    return "Brightness adjustment not implemented yet."

def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"Battery is at {battery.percent}% and {'plugged in' if battery.power_plugged else 'not plugged in'}."
    return "Battery status not available."
