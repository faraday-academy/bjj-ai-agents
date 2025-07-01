DB_FILE = bjj_app.db

.PHONY: reset-db create-db delete-db run run-dev

delete-db:
	rm -f $(DB_FILE)

create-db:
	python3 -c "from app.database import init_database; init_database()"

reset-db: delete-db create-db

run:
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 7861

# Run the app in development mode (with auto-reload)
run-dev:
	uv run python main.py
