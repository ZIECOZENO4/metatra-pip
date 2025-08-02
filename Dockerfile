FROM ubuntu:20.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wine \
    wine64 \
    wine32 \
    winbind \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up Wine environment
ENV WINEPREFIX=/root/.wine
ENV WINEARCH=win64

# Download and install Python for Windows
RUN wget https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe && \
    wine python-3.9.13-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python-3.9.13-amd64.exe

# Install MT5 in Wine Python
RUN wine python -m pip install MetaTrader5==5.0.5120

# Copy application files
COPY . /app
WORKDIR /app

# Install Python requirements
RUN pip3 install -r requirements.txt

# Expose port
EXPOSE 5000

# Run the application
CMD ["python3", "main_wine.py"] 