FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg from Python package instead of apt-get
RUN pip install --no-cache-dir ffmpeg-python

# Copy requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy bot source
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
