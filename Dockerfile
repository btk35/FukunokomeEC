FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#タイムゾーン（日本）
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
 && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
 && echo Asia/Tokyo > /etc/timezone \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリ本体
COPY . /app/

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]