clean: clean-build clean-pyc

clean-build: ## remove build artifacts
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.dist-info' -exec rm -fr {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +

vendor:
	rm -rf static_server/vendor
	mkdir -p static_server/vendor
	pip install -r static_server/requirements.txt -t static_server/vendor

build: vendor clean
	sam build

test:
	pipenv run python -m pytest tests/ -v

package: build
	sam package --s3-bucket $(bucketname)

run: build
	sam local start-api

deploy: package
	sam deploy -g