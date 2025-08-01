FROM python:3.12-slim
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "kedenbot.asgi:application", "--host=0.0.0.0", "--port=8000"]