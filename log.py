import json
import re
import time
from prometheus_client import start_http_server, Gauge, Counter

# Define a Prometheus metric
TOTAL_RESPONSE_SIZE = Gauge("traefik_downstream_content_size", "Total response size in bytes")
downstream_status_404 = Counter('downstream_status_404', 'Count of 404 DownstreamStatus')
downstream_status_499 = Counter('downstream_status_499', 'Count of 499 DownstreamStatus')
downstream_status_0 = Counter('downstream_status_0', 'Count of 0 DownstreamStatus')
downstream_status_502 = Counter('downstream_status_502', 'Count of 502 DownstreamStatus')
downstream_status_200 = Counter('downstream_status_200', 'Count of 200 DownstreamStatus')

# Prometheus counter for total status count
total_status_count = Counter('total_downstream_status_count', 'Total count of all DownstreamStatus')


def parse_traefik_logs(file_path):
    """Generator function to extract DownstreamContentSize from each log entry while handling null bytes."""
    with open(file_path, "r", encoding="utf-8-sig") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            # Remove null bytes and non-printable characters
            line = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', line)

            try:
                log_data = json.loads(line)  
                content = log_data.get("DownstreamContentSize", 0)  
                status = log_data.get("DownstreamStatus", None) 
                yield content, status
            except json.JSONDecodeError:
                continue  

def format_size(size_in_bytes):
    """Convert bytes to KB, MB, GB."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Bytes"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024**3:.2f} GB"

def update_prometheus_metrics(status):
    """Update Prometheus metrics based on DownstreamStatus."""
    # Update Prometheus counters for specific DownstreamStatus
    if status == 404:
        downstream_status_404.inc()
    elif status == 499:
        downstream_status_499.inc()
    elif status == 0:
        downstream_status_0.inc()
    elif status == 502:
        downstream_status_502.inc()
    elif status == 200:
        downstream_status_200.inc()

    # Increment the total status count
    total_status_count.inc()

def update_metrics(log_file):
    """Periodically update Prometheus metrics."""
    while True:
        total_size = 0
        for content, status in parse_traefik_logs(log_file):
            total_size += content
            if status is not None:
                update_prometheus_metrics(status)

        TOTAL_RESPONSE_SIZE.set(total_size)
        print(f"🔹 Total Response Size: {format_size(total_size)}")
        time.sleep(1)

if __name__ == "__main__":
    log_file = "traefik.log"

    # Start Prometheus metrics server on port 8000
    start_http_server(8000)

    # Update metrics continuously
    update_metrics(log_file)
