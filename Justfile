set dotenv-load

set shell := ["powershell.exe", "-Command"]
lint:
    uv run ruff check . --fix
    uv run ruff format .
    uv run ruff check .

test-all:
    python -m pytest -s 

api:
    uv run uvicorn src.main:app --reload

build:
    docker compose up --build

clean:
    docker compose down