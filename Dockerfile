# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
&& rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
&& pip install --no-cache-dir gunicorn


RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get clean


RUN pip install --upgrade pip


# Copy project files
COPY config.py .
COPY run.py .
COPY app/ ./app/

# Create any necessary directories
RUN mkdir -p instance

# Expose port
EXPOSE 8091

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8091", "run:app"]
