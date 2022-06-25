from aws_cdk import (
    CfnOutput,
    Stack
)
from aws_cdk import aws_apigateway as apigateway
from constructs import Construct
import json


class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = apigateway.RestApi(self, "Api",
            rest_api_name="CdkMockApi",
            disable_execute_api_endpoint=False,
            description="Sample API Gateway REST API with mock integration",
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL]
            )
        )

        deployment = apigateway.Deployment(self, "Deployment", api=api)

        # development stage
        apigateway.Stage(self, "dev",
            deployment=deployment,
            tracing_enabled=False,
            description="Dev Stage Deployment",
            stage_name="dev",
            metrics_enabled=True,
            method_options={
                "/*/*": apigateway.MethodDeploymentOptions(  # This special path applies to all resource paths and all HTTP methods
                    cache_data_encrypted=False,
                    caching_enabled=False,
                    data_trace_enabled=False,
                    metrics_enabled=True
                )
            }
        )

        mock = api.root.add_resource("mock")

        response_templates = {
            "statusCode": 200,
            "body": "ok",
            "accountId": "$context.accountId",
            "httpMethod": "$context.httpMethod",
            "stage": "$context.stage",
            "sourceIp": "$context.identity.sourceIp",
            "user": "$context.identity.user",
            "userAgent": "$context.identity.userAgent",
            "userArn": "$context.identity.userArn",
            "requestId": "$context.requestId"
        }
        request_templates = {
            "statusCode": 200,
            "context": {
                "accountId": "$context.identity.accountId",
                "apiId": "$context.apiId",
                "apiKey": "$context.identity.apiKey",
                "authorizerPrincipalId": "$context.authorizer.principalId",
                "caller": "$context.identity.caller",
                "cognitoAuthenticationProvider": "$context.identity.cognitoAuthenticationProvider",
                "cognitoAuthenticationType": "$context.identity.cognitoAuthenticationType",
                "cognitoIdentityId": "$context.identity.cognitoIdentityId",
                "cognitoIdentityPoolId": "$context.identity.cognitoIdentityPoolId",
                "httpMethod": "$context.httpMethod",
                "stage": "$context.stage",
                "sourceIp": "$context.identity.sourceIp",
                "user": "$context.identity.user",
                "userAgent": "$context.identity.userAgent",
                "userArn": "$context.identity.userArn",
                "requestId": "$context.requestId",
                "resourceId": "$context.resourceId",
                "resourcePath": "$context.resourcePath"
            }
        }

        mock.add_method("GET",
                        apigateway.MockIntegration(
                            integration_responses=[
                                apigateway.IntegrationResponse(
                                    status_code="200",
                                    response_templates={
                                        "application/json": json.dumps(response_templates)
                                    }
                                )
                            ],
                            passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
                            request_templates={
                                "application/json": json.dumps(request_templates)
                            }
                        ),
                        method_responses=[apigateway.MethodResponse(status_code="200")],
                        )

        CfnOutput(self, "stage endpoint", value=api.url)
        CfnOutput(self, "mock", value=api.url_for_path("/mock"))