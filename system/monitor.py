import psutil
import time
from PySide6.QtCore import QObject, Signal, QThread

class SystemMonitorWorker(QThread):
    stats_updated = Signal(dict)
    alert_triggered = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            try:
                battery = psutil.sensors_battery()
                battery_percent = battery.percent if battery else None
            except:
                battery_percent = None

            stats = {
                'cpu': cpu,
                'ram': ram,
                'disk': disk,
                'battery': battery_percent
            }
            
            self.stats_updated.emit(stats)
            
            # Simple threshold logic
            if ram > 85: self.alert_triggered.emit(f"High RAM Usage: {ram}%")
            if cpu > 90: self.alert_triggered.emit(f"High CPU Usage: {cpu}%")
            if disk > 90: self.alert_triggered.emit(f"High Disk Usage: {disk}%")
            if battery_percent is not None and battery_percent < 20:
                self.alert_triggered.emit(f"Low Battery: {battery_percent}%")
                
            time.sleep(2)
            
    def stop(self):
        self.running = False
        self.wait()
