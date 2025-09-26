"""Example deployment script for AWS Lambda using AWS CDK."""

from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class F3WorkoutServiceStack(Stack):
    """CDK Stack for F3 Workout Service Lambda deployment."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda function
        workout_lambda = _lambda.Function(
            self,
            "WorkoutServiceLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.lambda_handler",
            code=_lambda.Code.from_asset("./"),
            environment={
                "DB_HOST": "your-mysql-host.rds.amazonaws.com",
                "DB_PORT": "3306",
                "DB_USERNAME": "your-db-username",
                # Note: Use AWS Secrets Manager for the password in production
                "DB_PASSWORD": "your-db-password",
                "DB_NAME": "f3rva_workouts",
            },
        )

        # Create API Gateway
        api = apigateway.LambdaRestApi(
            self,
            "WorkoutServiceApi",
            handler=workout_lambda,
            proxy=True,
        )
