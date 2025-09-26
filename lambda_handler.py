"""AWS Lambda handler for the workout service."""

import logging
from typing import Any

from mangum import Mangum

from app.main import app

logger = logging.getLogger(__name__)

# Create Lambda handler
handler = Mangum(app, lifespan="off")


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AWS Lambda entry point.
    
    Args:
        event: Lambda event data
        context: Lambda context
        
    Returns:
        HTTP response
    """
    logger.info(f"Processing Lambda event: {event.get('httpMethod')} {event.get('path')}")

    try:
        response = handler(event, context)
        logger.info(f"Lambda response status: {response.get('statusCode')}")
        return response
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": '{"error": "Internal server error"}'
        }
