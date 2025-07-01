FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN touch /app/bjj_app.db && chmod 666 /app/bjj_app.db
EXPOSE 7861
CMD ["python", "app.py"]
