HOST=localhost
BROWSER=chrome
CI=1

# Windows require explicit env var setting
ifeq "$(OS)" "Windows_NT"
	VARSET=set HOST=$(HOST)&& set CI=$(CI)&&set BROWSER=$(BROWSER)&&
endif

install-dev:
	poetry install --with dev

lint:
	poetry run ruff ./pyasli

test:
	$(VARSET)poetry run pytest -v --tb=line --cov-report xml --cov-config .coveragerc --cov pyasli tests
