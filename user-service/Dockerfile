FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

WORKDIR /user-service

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
