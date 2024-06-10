help: ## Show this help.
	@ fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.PHONY: lint
lint: ## Run flake8 and mypy linting on the project
	@ echo "Checking code style with flake8..."
	@ flake8 --toml-config=../pyproject.toml
	@ echo "Checking types with mypy..."
	@ mypy .

.PHONY: black
black: ## Run black formatter on the project
	black . -l 120

.PHONY: test
test: ## Run tests
	pytest ../tests/**