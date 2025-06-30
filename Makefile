DB_FILE = bjj_app.db

.PHONY: reset-db create-db delete-db

delete-db:
	rm -f $(DB_FILE)

create-db:
	python3 -c "from app.database import init_database; init_database()"

reset-db: delete-db create-db
