.PHONY: all
all: start

.PHONY: start
start:
	@echo "Starting Oracle database container..."
	@docker compose up --wait --detach oracle
	@echo "Oracle database is running at localhost:15211"
	@echo "Database: FREEPDB1"
	@echo "Username: scott"
	@echo "Password: tiger"

.PHONY: clean
clean:
	@docker compose down --volumes --rmi local
	@echo "Cleaned up project containers, volumes, and locally built images"