FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN touch /app/bjj_app.db
RUN chown -R 1000:1000 /app
USER 1000
EXPOSE 7861
CMD ["python", "main.py"]
