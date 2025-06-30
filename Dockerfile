FROM python:3.10-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY . .

RUN pip install uv

RUN uv pip install --system .

EXPOSE 7860

CMD ["uvicorn", "main:demo", "--host", "0.0.0.0", "--port", "7860"]
