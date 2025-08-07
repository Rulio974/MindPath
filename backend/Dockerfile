FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "main.py", "--mode", "api", "--rerank", "--top_k", "5"]
