FROM python:3.12-slim-bookworm

# Prevent Python from writing .pyc files to disk and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

# Command to run your application using app_api.py
CMD ["python", "app_api.py"]