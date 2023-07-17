CONDA_ENV = pylox

generate_ast:
	conda run -n $(CONDA_ENV) python3 src/tools/generate_ast.py

.PHONY: generate_ast