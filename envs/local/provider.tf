terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.15.0"
    }
    archive = {
      source  = "hashicorp/archive",
      version = "2.7.1"
    }
  }
  required_version = "1.13.3"
}

provider "aws" {
  region     = "ap-northeast-1"

  # Manual Configuration required when not using tflocal
  # https://docs.localstack.cloud/aws/integrations/infrastructure-as-code/terraform/#manual-configuration
  access_key = "dummy"
  secret_key = "dummy"

  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    logs   = "http://localhost:4566"
    iam    = "http://localhost:4566"
    lambda = "http://localhost:4566"
    s3     = "http://localhost:4566"
  }
}
