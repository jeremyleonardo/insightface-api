# Insightface API

## About

A simple <a href="https://github.com/deepinsight/insightface">deepinsight/insightface</a> implementation with <a href="https://github.com/tiangolo/fastapi">FastAPI</a> for face verification.

## Possible Improvements
- [ ] Use a proper db migration package such as alembic

## Available APIs

It is recommended to test the available APIs from ``[GET] /docs``

- ``[GET] /`` - Root
  - Check API status

- ``[POST] /upload-selfie`` - Upload Selfie
  - Upload selfie image file with person name and store it to database

- ``[POST] /face-verification`` - Face Verification
  - Upload selfie image file and a person name from the database to verify

- ``[POST] /face-search`` - Face Search
  - Upload selfie image file to search for similar faces in database

- ``[PUT] /faces`` - Update Face
  - Update face data (name or face data) in the database

- ``[GET] /faces`` - Get Faces
  - Get faces from database

- ``[DELETE] /faces`` - Delete Face
  - Delete a face from database using name from database

- ``[POST] /analyze-image-url`` - Analyze Image Url
  - Send image url to analyze (does not save to database)

- ``[POST] ​/analyze-image-file`` - Analyze Image File
  - Upload image file to analyze (does not save to database)

- ``[POST] /compute-selfie-image-files-similarity`` -  Compute Selfie Image Files Similarity
  - Compute similarity of 2 selfie image files (does not save to database)

## Quickstart

Using docker-compose (RECOMMENDED):
```
docker-compose up
```

Using pipenv (you'll need to setup postgresql and .env on your own):
```
pipenv run uvicorn app.main:app --reload
```

Using poetry (you'll need to setup postgresql and .env on your own):
```
poetry run uvicorn app.main:app --reload
```

## Models

You can download the model files and move them into `~/.insightface/models`

Original source:
- arcface_r100_v1 : http://insightface.ai/files/models/arcface_r100_v1.zip
- genderage_v1 : http://insightface.ai/files/models/genderage_v1.zip
- retinaface_r50_v1 : http://insightface.ai/files/models/retinaface_r50_v1.zip

Alternative:
- https://github.com/jeremy-leonardo/insightface-models
