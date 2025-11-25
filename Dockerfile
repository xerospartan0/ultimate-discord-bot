FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg build-essential libffi-dev libpq-dev && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]
