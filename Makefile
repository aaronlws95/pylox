.ONESHELL:
SHELL = /bin/bash
CONDA_ENV = pylox
CONDA_RUN = conda run -n $(CONDA_ENV)
CONDA_PATH = $$(conda info --base)/etc/profile.d/conda.sh
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE  = conda activate ; conda activate ${CONDA_ENV}
conda: 
	conda create -n ${CONDA_ENV} python=3.10 -y
	source ${CONDA_PATH}
	${CONDA_ACTIVATE}
	pip install -r requirements.txt

build:
	$(CONDA_RUN) python3 src/tools/generate_ast.py

test: build
	$(CONDA_RUN) tox -e unittest

coverage: test
	$(CONDA_RUN) coverage report -m

format: 
	$(CONDA_RUN) tox -e format
	$(CONDA_RUN) tox -e lint

.PHONY: conda format build test coverage