# Set immagine base per l'OS
FROM sampeka/ffmpeg-python:3.6.5-slim

# Directory nella quale imposto l'ambiente di lavoro
WORKDIR /app

# Copia dei requisiti di sistema
COPY requirements.txt .

# Installo le dipendenze di Python
RUN pip install --no-cache-dir -r requirements.txt

# Rimuovo le dipendenze una volta installate
RUN rm requirements.txt

# Copia del /src all'interno di /app/src
RUN mkdir src
COPY src/ ./src

# Buona visione!
CMD [ "python", "src/main.py" ]

