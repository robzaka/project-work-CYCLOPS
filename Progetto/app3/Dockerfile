FROM python:3.10-slim

WORKDIR /app

# Librerie di sistema minime richieste da pillow e torchvision
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Installa le librerie Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice e i file del progetto
COPY . .

EXPOSE 5000

CMD ["python", "app3.py"]
