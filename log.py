import json
import re
from prometheus_client import start_http_server, Gauge
import time

# Define a Prometheus metric
TOTAL_RESPONSE_SIZE = Gauge("traefik_downstream_content_size", "Total response size in bytes")

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
                yield log_data.get("DownstreamContentSize", 0)  
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

def update_metrics(log_file):
    """Periodically update Prometheus metrics."""
    while True:
        total_size = sum(parse_traefik_logs(log_file))
        TOTAL_RESPONSE_SIZE.set(total_size)  # Update Prometheus metric
        formatted_size = format_size(total_size)
        print(f"🔹 Total Response Size: {formatted_size}")

        time.sleep(1)  # Update every 10 seconds

if __name__ == "__main__":
    log_file = "traefik.log"

    # Start Prometheus metrics server on port 8000
    start_http_server(8000)

    # Update metrics continuously
    update_metrics(log_file)
