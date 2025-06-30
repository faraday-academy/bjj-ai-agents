FROM python:3.10-slim AS builder

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv pip compile pyproject.toml -o requirements.txt

FROM python:3.10-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY --from=builder /code/requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "main:demo", "--host", "0.0.0.0", "--port", "7860"]
