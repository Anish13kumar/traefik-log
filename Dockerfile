# Use an official lightweight Python image
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY log.py .

# Expose the Prometheus metrics port
EXPOSE 8000

# Run the script
CMD ["tail", "-f", "/dev/null"]
