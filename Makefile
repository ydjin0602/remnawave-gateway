PORT:=8000

run:
	uvicorn app.main:app --host 127.0.0.1 --port "$(PORT)"

test:
	pytest --maxfail=1 -vv

lint:
	pre-commit run --all-files
