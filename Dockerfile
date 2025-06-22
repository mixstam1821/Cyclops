# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the port for Bokeh (default 5006, but let's use 8000 for wider compatibility)
EXPOSE 8000

# Run Bokeh server
CMD ["bokeh", "serve", "--allow-websocket-origin=*", "--port=8000", "--address=0.0.0.0", "Cyclops.py"]
