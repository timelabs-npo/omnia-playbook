.PHONY: validate diagnose report test

validate:
	./scripts/validate.sh

diagnose:
	./scripts/diagnose.sh

report:
	./scripts/report.sh

test:
	python3 -m unittest discover -s tests -p 'test_*.py'
