.PHONY: all
all: start import-dashboards

.PHONY: import-dashboards
import-dashboards:
	@./superset/init/import-dashboards.sh > /dev/null

.PHONY: start
start:
	@docker compose build
	@docker compose up -d

	@until nc -z localhost 8088; do sleep 1; done

	@echo "Initializing Superset..."
	@./superset/init/init.sh > /dev/null

	@echo ""
	@echo "Superset is running at http://localhost:8088, login with admin/admin"

.PHONY: clean
clean:
	@docker compose down --volumes --rmi local
	@echo "Cleaned up project containers, volumes, and locally built images"