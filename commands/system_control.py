import os
import ctypes
import psutil
import subprocess
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc


def shutdown():
    os.system("shutdown /s /t 1")
    return "Shutting down the system."


def restart():
    os.system("shutdown /r /t 1")
    return "Restarting the system."


def set_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, 0, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    current_volume = volume.GetMasterVolumeLevelScalar() * 100

    # If level is greater than the current volume
    if level > current_volume:
        for i in range(int(current_volume), int(level), 1):
            volume.SetMasterVolumeLevelScalar(i / 100, None)
    # If level is less than the current volume
    elif level < current_volume:
        for i in range(int(current_volume), int(level), -1):
            volume.SetMasterVolumeLevelScalar(i / 100, None)

    return f"Volume set to {level}%."


def set_brightness(level):
    current_brightness = sbc.get_brightness()[0]
    
    # Gradually change brightness
    if level > current_brightness:
        for i in range(current_brightness, level, 1):
            sbc.set_brightness(i)
    elif level < current_brightness:
        for i in range(current_brightness, level, -1):
            sbc.set_brightness(i)

    return f"Brightness set to {level}%."


def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"Battery is at {battery.percent}% and {'plugged in' if battery.power_plugged else 'not plugged in'}."
    return "Battery status not available."


def lock_system():
    try:
        ctypes.windll.user32.LockWorkStation()
        return "System locked successfully."
    except Exception as e:
        return f"Failed to lock system: {str(e)}"


def toggle_wifi(turn_on=True):
    try:
        state = "on" if turn_on else "off"
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", state], check=True)
        return f"Wi-Fi turned {state} successfully."
    except Exception as e:
        return f"Failed to toggle Wi-Fi: {str(e)}"


def toggle_airplane_mode(turn_on=True):
    try:
        if turn_on:
            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disable"], check=True)
            return "Airplane Mode activated (Wi-Fi disabled)."
        else:
            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enable"], check=True)
            return "Airplane Mode deactivated (Wi-Fi enabled)."
    except Exception as e:
        return f"Failed to toggle Airplane Mode: {str(e)}"
