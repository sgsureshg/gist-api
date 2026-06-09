# GitHub Gists API

## Overview
A simple Flask API that returns public GitHub gists for a user.

## Endpoint

GET /<username>

## Run locally


python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

Server runs on:
http://localhost:8080

## Run tests

pytest

## Run with Docker

docker build -t gists-api .
docker run -p 8080:8080 gists-api

## Notes
- Uses GitHub public API
- Supports rate limiting and basic error handling