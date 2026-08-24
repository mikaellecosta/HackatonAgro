# =============================================================================
# Grupo Tereza — atalhos de desenvolvimento
# =============================================================================
TAILWIND     := ./bin/tailwindcss
TW_INPUT     := frontend/static/css/tailwind.input.css
TW_OUTPUT    := frontend/static/css/tailwind.css

.PHONY: tailwind tailwind-watch tailwind-min run

# Build único, minificado — use antes de commitar/deploy
tailwind:
	$(TAILWIND) -i $(TW_INPUT) -o $(TW_OUTPUT) --minify

# Modo desenvolvimento — recompila a cada save num template
tailwind-watch:
	$(TAILWIND) -i $(TW_INPUT) -o $(TW_OUTPUT) --watch

# Sobe o servidor Django
run:
	python manage.py runserver
