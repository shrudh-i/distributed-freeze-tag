# Use Python base image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    liblcm-dev \
    python3-dev \
    python3-pip \
    pkg-config \
    libpython3-dev \
    python3-pygame \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all source files
COPY *.py /app/
COPY messages.lcm /app/

# Generate LCM Python bindings
RUN lcm-gen -p messages.lcm

# Install Python dependencies
RUN pip3 install lcm pygame

# Make the entry script executable
RUN chmod +x /app/game.py

# # Create a startup script that uses host display
# RUN echo '#!/bin/bash\nexec python3 game.py "$@"' > /app/start.sh && \
#     chmod +x /app/start.sh

# # Use the startup script as entrypoint
# ENTRYPOINT ["/app/start.sh"]

# Command to run by default - arguments will be passed after the image name
ENTRYPOINT ["python3", "game.py"]