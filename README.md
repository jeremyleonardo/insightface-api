# Insightface API

## About

A simple <a href="https://github.com/deepinsight/insightface">deepinsight/insightface</a> implementation with <a href="https://github.com/tiangolo/fastapi">FastAPI</a> for face verification.

## Instructions

1. Create your own .env using .env.example
2. Replace placeholder ``DATABASE_URL`` with your postgresql database url

## Starting

Using pipenv:
```
pipenv run uvicorn app.main:app --reload
```
