import platform
import psutil
import datetime


def get_system_info():
    """Get detailed system information."""
    try:
        # System Information
        info = {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            
            # Memory Information
            "Total RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
            "Available RAM": f"{round(psutil.virtual_memory().available / (1024 ** 3), 2)} GB",
            "RAM Usage": f"{psutil.virtual_memory().percent}%",
            
            # CPU Information
            "CPU Cores": psutil.cpu_count(),
            "CPU Usage": f"{psutil.cpu_percent()}%",
            
            # Disk Information
            "Disk Usage": f"{psutil.disk_usage('/').percent}%",
            
            # Boot Time
            "Boot Time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        }

        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    except Exception as e:
        return f"Error getting system information: {str(e)}"
