.PHONY: run test install lint

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

test:
	pytest tests/ -v

lint:
	python -m py_compile app.py utils/data_loader.py utils/map_builder.py utils/validators.py && echo "✅ No syntax errors"
