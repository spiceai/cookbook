.PHONY: all
all: start

.PHONY: start
start:
	@echo "Starting Dremio container..."
	@docker compose up --detach
	@./setup-dremio.sh

.PHONY: clean
clean:
	@docker compose down --volumes --rmi local
	@rm -rf .spice
	@echo "Cleaned up project containers, volumes, and locally built images"
