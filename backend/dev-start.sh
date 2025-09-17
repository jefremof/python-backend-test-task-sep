#!/bin/bash
alembic upgrade head
python -m src.scripts.seed
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload