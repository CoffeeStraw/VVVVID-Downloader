# Set immagine base per l'OS
FROM sampeka/ffmpeg-python:3.6.5-slim

# Directory nella quale imposto l'ambiente di lavoro
WORKDIR /vvvvid-dowloader

# Copia dei requisiti di sistema
COPY requirements.txt .

# Installo le dipendenze di Python
RUN pip install --no-cache-dir -r requirements.txt  

# Rimuovo le dipendenze una volta installate
RUN rm requirements.txt

# Copia del /src all'interno dell'attuale ambiente di lavoro
COPY src/ .

# # Buona visione!
CMD [ "python", "main.py"]