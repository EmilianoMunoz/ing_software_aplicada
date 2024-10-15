FROM python:3.10-slim

# Actualiza los paquetes del sistema
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    # Si necesitas algún paquete adicional, lo puedes agregar aquí
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]

