
/*  This sample code is based on the example found on the Hashicorp website at 
    https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api
*/


resource "aws_api_gateway_rest_api" "api" {
  name = var.api_name
  description = "Sample API Gateway REST API with mock integration created with Terraform"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  disable_execute_api_endpoint = false
}

resource "aws_api_gateway_resource" "mock" {
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "mock"
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "mock" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.mock.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method_response" "mock_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.mock.id
  http_method = aws_api_gateway_method.mock.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration" "mock" {
  http_method = aws_api_gateway_method.mock.http_method
  resource_id = aws_api_gateway_resource.mock.id
  rest_api_id = aws_api_gateway_rest_api.api.id
  type        = "MOCK"
    request_templates = {
        "application/json" = file("${path.module}/templates/request.json")
    }
}
resource "aws_api_gateway_integration_response" "mock" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.mock.id
  http_method = aws_api_gateway_method.mock.http_method
  status_code = aws_api_gateway_method_response.mock_200.status_code

  # Transforms the backend JSON response to XML
  response_templates = {
    "application/json" = file("${path.module}/templates/response.json")
    }
}
resource "aws_api_gateway_deployment" "mock" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.mock.id,
      aws_api_gateway_method.mock.id,
      aws_api_gateway_integration.mock.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "mock" {
  deployment_id = aws_api_gateway_deployment.mock.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "dev"
}