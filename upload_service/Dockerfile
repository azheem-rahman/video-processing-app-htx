FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    build-essential \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

COPY ../db ./db
COPY . .

COPY upload_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "upload_service.main:app", "--host", "0.0.0.0", "--port", "8000"]