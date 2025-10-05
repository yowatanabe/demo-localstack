module "lambda" {
  source        = "../../modules/lambda"
  function_name = "demo-local-lambda"
  environment = {
    ENVIRONMENT     = "local"
    DOJO_URL        = "http://host.docker.internal:8080"
    DOJO_TOKEN      = var.dojo_token
    PRODUCT_NAME    = "demo-app"
    ENGAGEMENT_NAME = "demo-engagement"
  }
}

module "s3" {
  source               = "../../modules/s3"
  bucket_name          = "demo-local-bucket"
  lambda_function_name = module.lambda.function_name
  lambda_function_arn  = module.lambda.function_arn
}
