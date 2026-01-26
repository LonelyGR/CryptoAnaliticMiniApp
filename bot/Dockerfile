FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY reminders_worker.py ./reminders_worker.py
COPY bot_service.py ./bot_service.py

CMD ["python", "bot_service.py"]

