# Insightface API

## About

A simple <a href="https://github.com/deepinsight/insightface">deepinsight/insightface</a> implementation with <a href="https://github.com/tiangolo/fastapi">FastAPI</a> for face verification.

## Instructions

1. Create your own .env using .env.example
2. Replace placeholder ``DATABASE_URL`` with your postgresql database url

## Starting

Using docker-compose:
```
docker-compose up
```
Using pipenv (you'll need to setup postgresql on your own):
```
pipenv run uvicorn app.main:app --reload
```

## Models

Optional: Download & extract everything and put it on the models folder only if you're using docker-compose

Original source:
- arcface_r100_v1 : http://insightface.ai/files/models/arcface_r100_v1.zip
- genderage_v1 : http://insightface.ai/files/models/genderage_v1.zip
- retinaface_r50_v1 : http://insightface.ai/files/models/retinaface_r50_v1.zip

Alternative:
- https://github.com/jeremy-leonardo/insightface-models

