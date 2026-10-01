.PHONY: all
all: start

.PHONY: start
start:
	@echo "Starting PostgreSQL container..."
	@docker compose up --detach --wait
	@docker compose exec postgres psql -U postgres -d taxi -c 'SELECT COUNT(*) AS taxi_zones FROM taxi_zones;'

.PHONY: clean
clean:
	@docker compose down --volumes --rmi local
	@rm -rf .spice
	@echo "Cleaned up project containers, volumes, and locally built images"
