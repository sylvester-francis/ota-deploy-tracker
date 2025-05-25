FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command runs the API server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
