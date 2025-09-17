VENV_PATH = backend

format:
	uv run ruff format backend/src/

check:
	uv run ruff check src/ main.py;
	uv run mypy src/ main.py

test:
	uv run pytest

pip_fix:
	.\.venv\Scripts\python.exe -m ensurepip --upgrade
	.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

