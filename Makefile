# LocalStack Demo - Makefile
# Build and deployment management for Lambda function that sends Semgrep results to DefectDojo

.PHONY: build clean plan apply destroy

# Build Lambda package to build/ directory
build:
	rm -rf build
	mkdir -p build
	cp src/handler.py build/
	cd build && pip install -r ../src/requirements.txt -t .

# Execute LocalStack Plan
plan:
	cd envs/local && tflocal plan

# Create resources in LocalStack
apply:
	cd envs/local && tflocal init && tflocal apply

# Delete LocalStack resources
destroy:
	cd envs/local && tflocal destroy
