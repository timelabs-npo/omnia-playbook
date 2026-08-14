.PHONY: validate diagnose report test compile-bus verify-bus

validate:
	./scripts/validate.sh

diagnose:
	./scripts/diagnose.sh

report:
	./scripts/report.sh

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

compile-bus:
	python3 tools/build_bus_fixtures.py

verify-bus: compile-bus
	python3 -m unittest tests.test_omnia_bus -v
	git diff --exit-code -- artifacts/omnia-bus-v1
