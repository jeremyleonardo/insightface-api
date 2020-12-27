# Insightface API

## About

A simple <a href="https://github.com/deepinsight/insightface">deepinsight/insightface</a> implementation with <a href="https://github.com/tiangolo/fastapi">FastAPI</a> for face verification.

## Available APIs

- ``[GET] /`` - Root
  - Check API status

- ``[POST] /upload-selfie`` - Upload Selfie
  - Upload selfie image file with person name and store it to database

- ``[POST] /face-verification`` - Face Verification
  - Upload selfie image file and a person name from the database to verify

- ``[POST] /analyze-image-url`` - Analyze Image Url
  - Send image url to analyze

- ``[POST] ​/analyze-image-file`` - Analyze Image File
  - Upload image file to analyze

- ``[POST] /compute-selfie-image-files-similarity`` -  Compute Selfie Image Files Similarity
  - Compute similarity of 2 selfie image files

- ``[PUT] /faces`` - Update Face
  - Update face data (name or face data)

- ``[GET] /faces`` - Get Faces
  - Get faces

- ``[DELETE] /faces`` - Delete Face
  - Delete a face from database using name

## Starting

Using docker-compose:
```
docker-compose up
```
Using pipenv (you'll need to setup postgresql and .env on your own):
```
pipenv run uvicorn app.main:app --reload
```

## Docker Compose

docker-compose.yml
```yml
version: "3.8"
   
services:
  web:
    image: jeremyleo/insightface-api:latest
    command: pipenv run uvicorn app.main:app --host 0.0.0.0 --port 80
    volumes:
      - ./models:/root/.insightface/models
    ports:
      - "80:80"
    depends_on:
      - db
    environment: 
      - DATABASE_URL=postgres://postgres:password@db/insightface_db
  db:
    image: postgres:13.1
    ports:
      - '5432:5432'
    environment:
      - POSTGRES_DB=insightface_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password

```

## Models

Optional: Download & extract everything and put it on the models folder only if you're using docker-compose

Original source:
- arcface_r100_v1 : http://insightface.ai/files/models/arcface_r100_v1.zip
- genderage_v1 : http://insightface.ai/files/models/genderage_v1.zip
- retinaface_r50_v1 : http://insightface.ai/files/models/retinaface_r50_v1.zip

Alternative:
- https://github.com/jeremy-leonardo/insightface-models

