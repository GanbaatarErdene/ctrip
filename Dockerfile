FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.9.6-slim-buster

# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# COPY requirements.txt requirements.txt

# RUN pip install --upgrade pip

# RUN pip install -r requirements.txt

# COPY . /app

# ENV PYTHONPATH "${PYTHONPATH}:/app"

# EXPOSE 8000
