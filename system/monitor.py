import psutil

class SystemMonitor:
    def get_stats(self):
        return {
            'cpu': psutil.cpu_percent(interval=0.1),
            'ram': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
