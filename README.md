# demo-localstack

A demo serverless application that integrates Semgrep with DefectDojo using LocalStack.

## Overview

This serverless application automatically sends Semgrep scan results to DefectDojo when scan result files are uploaded to an S3 bucket via Lambda function.

## Prerequisites

- LocalStack CLI
- awslocal
- tflocal
- Docker
- Terraform

## Installation

### LocalStack CLI

```bash
brew install localstack/tap/localstack-cli
```

### awslocal and tflocal

```bash
pip install awscli-local
pip install terraform-local
```

## Setup

### 1. Start DefectDojo

Refer to [Quick Start for Compose V2](https://github.com/DefectDojo/django-DefectDojo?tab=readme-ov-file#quick-start-for-compose-v2)

Create `Product` and `Engagement` in advance:

- **Product**: `demo-app`
- **Engagement**: `demo-engagement`

Get the API Key from `API v2 Key`.

### 2. Environment Variables

Copy `envs/local/terraform.tfvars.template` to create `terraform.tfvars` and set your DefectDojo API v2 key.

```bash
cp envs/local/terraform.tfvars.template envs/local/terraform.tfvars
```

### 3. Start LocalStack

```bash
localstack start -d
localstack status
```

### 4. Deploy

```bash
# Build
make build

# Deploy
make apply
```

### 5. Verify Resources

```bash
# Check S3 bucket
awslocal s3 ls

# Check Lambda function
awslocal lambda get-function-configuration --function-name demo-local-lambda
```

## Usage

### 1. Run Semgrep Scan

```bash
# Clone OWASP Juice Shop source code
git clone https://github.com/juice-shop/juice-shop.git

# Run Semgrep and save the results
docker run --rm -v "${PWD}:/src" semgrep/semgrep semgrep \
  --config=auto --json -o /src/semgrep_results.json juice-shop/
```

### 2. Upload Scan Results

```bash
# Upload to S3
awslocal s3 cp semgrep_results.json s3://demo-local-bucket

# Check Lambda function logs
awslocal logs tail /aws/lambda/demo-local-lambda
```

### 3. Verify DefectDojo

Check that a `Test` has been added to the `Engagement`.

## Cleanup

```bash
# Delete resources
make destroy

# Stop LocalStack
localstack stop
```

## References

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [Semgrep DefectDojo Integration](https://semgrep.dev/docs/kb/integrations/defect-dojo-integration)
- [DefectDojo Quick Start](https://github.com/DefectDojo/django-DefectDojo?tab=readme-ov-file#quick-start-for-compose-v2)
