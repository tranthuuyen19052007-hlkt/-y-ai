FROM python:3.11-slim

WORKDIR /app

# Copy toan bo ma nguon vao container
COPY . /app

# Khong can pip install vi du an khong co thu vien ngoai (Zero-dependency)
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

CMD ["python", "app.py"]

