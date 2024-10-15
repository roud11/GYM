FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "Base.py"]