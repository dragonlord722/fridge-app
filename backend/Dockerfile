# 1. Start with the Base Image (MUST BE FIRST)
FROM python:3.11-slim

# 2. Set Environment Variables (Unbuffers logs for Cloud Run)
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your application code
COPY . .

# 6. Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]