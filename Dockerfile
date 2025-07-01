FROM python:3.10-slim AS builder

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN pip install uv

# TODO: Some generated dependency versions are not working, so we're using the current requirements.txt file instead
# RUN uv pip compile pyproject.toml -o requirements.txt

FROM python:3.10-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY --from=builder /code/requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7861

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","7861"]
