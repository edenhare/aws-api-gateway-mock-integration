/*
    Declare all of the outputs used in the project in this file
*/

output "mock_path" {
    value =  aws_api_gateway_resource.mock.path
}

output "stage_url" {
    value = aws_api_gateway_stage.mock.invoke_url
}

output "mock_endpoint" {
    value = join("", [aws_api_gateway_stage.mock.invoke_url, aws_api_gateway_resource.mock.path])
}