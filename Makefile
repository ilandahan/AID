# AI Full Stack Development Methodology - Makefile
#==============================================================================

.PHONY: install setup clean test verify docs help

# Default target
.DEFAULT_GOAL := help

# Variables
SKILLS_DIR := $(HOME)/.claude/skills
CLAUDE_CONFIG := $(HOME)/.claude
SHELL := /bin/bash

#------------------------------------------------------------------------------
# Installation targets
#------------------------------------------------------------------------------

install: ## Run full installation
	@./install.sh

install-deps: ## Install npm dependencies (puppeteer, etc.)
	@npm install
	@echo "Dependencies installed (including puppeteer + Chromium)"

setup: setup-dirs setup-env install-deps setup-skills setup-config ## Setup without npm dependencies
	@echo "Setup complete!"

setup-dirs: ## Create necessary directories
	@mkdir -p $(SKILLS_DIR)
	@mkdir -p $(CLAUDE_CONFIG)
	@echo "Directories created"

setup-env: ## Setup environment file
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example - please edit with your values")

setup-skills: ## Install skills to Claude directory
	@for skill in skills/*/; do \
		skill_name=$$(basename $$skill); \
		echo "Installing skill: $$skill_name"; \
		cp -r $$skill $(SKILLS_DIR)/; \
	done
	@echo "Skills installed to $(SKILLS_DIR)"

setup-config: ## Copy Claude configuration
	@cp -n .claude/settings.json $(CLAUDE_CONFIG)/settings.local.json 2>/dev/null || true
	@echo "Configuration copied"

#------------------------------------------------------------------------------
# MCP Server targets
#------------------------------------------------------------------------------

mcp-install: ## Pre-install MCP servers for faster startup
	@echo "Pre-installing MCP servers..."
	@npx -y @modelcontextprotocol/server-atlassian --help >/dev/null 2>&1 || true
	@npx -y @modelcontextprotocol/server-github --help >/dev/null 2>&1 || true
	@npx -y @modelcontextprotocol/server-postgres --help >/dev/null 2>&1 || true
	@npx -y @modelcontextprotocol/server-filesystem --help >/dev/null 2>&1 || true
	@npx -y chrome-devtools-mcp@latest --help >/dev/null 2>&1 || true
	@echo "MCP servers pre-installed"

mcp-verify: ## Verify MCP configuration
	@echo "Checking MCP configuration..."
	@test -f .mcp.json && echo "✓ .mcp.json exists" || echo "✗ .mcp.json missing"
	@test -f .env && echo "✓ .env exists" || echo "✗ .env missing (copy from .env.example)"
	@cat .mcp.json 2>/dev/null | head -20 || true

#------------------------------------------------------------------------------
# Docker targets
#------------------------------------------------------------------------------

docker-up: ## Start PostgreSQL and pgAdmin containers
	@docker-compose up -d postgres pgadmin
	@echo "Database services started"
	@echo "PostgreSQL: localhost:5432"
	@echo "pgAdmin: http://localhost:5050"

docker-down: ## Stop Docker containers
	@docker-compose down
	@echo "Docker containers stopped"

docker-logs: ## View Docker container logs
	@docker-compose logs -f

docker-clean: ## Stop containers and remove volumes
	@docker-compose down -v
	@echo "Containers stopped and volumes removed"

docker-build: ## Build and start all services (production)
	@docker-compose --profile production up -d --build
	@echo "Production services started"

#------------------------------------------------------------------------------
# Verification targets
#------------------------------------------------------------------------------

verify: ## Verify installation
	@echo "Verifying installation..."
	@echo ""
	@echo "Configuration files:"
	@test -f .mcp.json && echo "  ✓ .mcp.json (MCP servers)" || echo "  ✗ .mcp.json missing"
	@test -f .env && echo "  ✓ .env (environment)" || echo "  ✗ .env missing"
	@test -f .claude/settings.json && echo "  ✓ .claude/settings.json" || echo "  ✗ .claude/settings.json missing"
	@echo ""
	@echo "Global installation:"
	@test -d $(SKILLS_DIR) && echo "  ✓ Skills directory exists" || echo "  ✗ Skills directory missing"
	@test -f $(CLAUDE_CONFIG)/settings.local.json && echo "  ✓ Global config exists" || echo "  ✗ Global config missing"
	@ls -1 $(SKILLS_DIR) 2>/dev/null | wc -l | xargs -I {} echo "  ✓ {} skills installed"

check-prereqs: ## Check prerequisites
	@echo "Checking prerequisites..."
	@command -v node >/dev/null && echo "✓ Node.js: $$(node -v)" || echo "✗ Node.js not found"
	@command -v npm >/dev/null && echo "✓ npm: $$(npm -v)" || echo "✗ npm not found"
	@command -v python3 >/dev/null && echo "✓ Python: $$(python3 --version)" || echo "✗ Python not found"
	@command -v git >/dev/null && echo "✓ Git: $$(git --version)" || echo "✗ Git not found"

#------------------------------------------------------------------------------
# Development targets
#------------------------------------------------------------------------------

test: ## Run tests (if any)
	@echo "Running tests..."
	@python3 -m pytest testing/ -v 2>/dev/null || echo "No tests found or pytest not installed"

lint: ## Run linters
	@echo "Running linters..."
	@find . -name "*.py" -exec python3 -m py_compile {} \; 2>/dev/null || true
	@echo "Lint complete"

#------------------------------------------------------------------------------
# Project initialization
#------------------------------------------------------------------------------

new-project: ## Initialize a new project (usage: make new-project NAME=my-project)
ifndef NAME
	@echo "Usage: make new-project NAME=my-project"
	@exit 1
endif
	@./scripts/init-project.sh $(NAME)

#------------------------------------------------------------------------------
# Documentation
#------------------------------------------------------------------------------

docs: ## Generate documentation index
	@echo "Documentation available in ./docs/"
	@echo ""
	@echo "Quick links:"
	@echo "  - MCP Setup: docs/mcp-setup.md"
	@echo "  - Phases: docs/phases/"
	@echo "  - Prompts: docs/prompts/"

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

clean: ## Clean temporary files
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned temporary files"

clean-install: ## Remove installed skills and config
	@rm -rf $(SKILLS_DIR)
	@rm -f $(CLAUDE_CONFIG)/settings.local.json
	@echo "Cleaned installation"

clean-recordings: ## Delete test recordings older than 7 days
	@echo "Cleaning old test recordings..."
	@find test-recordings/ -type f -not -name ".gitkeep" -not -name "README.md" -mtime +7 -delete 2>/dev/null || true
	@echo "Old recordings cleaned"

clean-all-recordings: ## Delete ALL test recordings (keep directory structure)
	@echo "Deleting all test recordings..."
	@find test-recordings/ -type f -not -name ".gitkeep" -not -name "README.md" -delete 2>/dev/null || true
	@echo "All recordings deleted"

#------------------------------------------------------------------------------
# Help
#------------------------------------------------------------------------------

help: ## Show this help message
	@echo "AI Full Stack Development Methodology"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
