.PHONY: all
all:
	@docker compose build
	@docker compose up -d

.PHONY: clean
clean:
	@docker compose down --volumes --rmi local
	@echo "Cleaned up project containers, volumes, and locally built images"