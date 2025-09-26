# F3RVA Workout Service

A modern Python microservice API for managing F3RVA workout information. Built with FastAPI and designed for AWS Lambda deployment.

## Features

- **Modern API Design**: Built with FastAPI following REST API best practices
- **AWS Lambda Ready**: Configured for serverless deployment with Mangum
- **Database Integration**: MySQL database support with connection pooling
- **Comprehensive Testing**: Unit tests with pytest and high code coverage
- **Code Quality**: Linting with Ruff, formatting with Black, type checking with MyPy
- **Health Monitoring**: Built-in health check endpoints
- **Validation**: Pydantic models for request/response validation
- **Error Handling**: Proper error handling and logging

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Get Workout by Date and Slug
```
GET /api/v1/workouts/{year}/{month}/{day}/{url_slug}
```

### Search Workout (POST)
```
POST /api/v1/workouts/search
Content-Type: application/json

{
  "year": 2024,
  "month": 1,
  "day": 15,
  "url_slug": "workout-slug"
}
```

## Data Models

### Workout Response
```json
{
  "success": true,
  "message": "Workout data retrieved successfully",
  "data": {
    "workout_date": "2024-01-15",
    "qic": {
      "name": "Ripken",
      "f3_name": "Cal Ripken Jr."
    },
    "pax": [
      {
        "name": "Donatello",
        "f3_name": "Donatello TMNT"
      }
    ],
    "aos": [
      {
        "name": "Warm-Up",
        "description": "Getting loose"
      },
      {
        "name": "The Thang",
        "description": "Main workout"
      }
    ],
    "url_slug": "ripken-beatdown-2024-01-15"
  }
}
```

## Database Schema

The service expects MySQL tables with the following structure (placeholders):

### workouts table
- workout_date (DATE)
- url_slug (VARCHAR)
- qic_name (VARCHAR)
- qic_f3_name (VARCHAR, nullable)

### pax table
- id (INT, primary key)
- pax_name (VARCHAR)
- f3_name (VARCHAR, nullable)

### aos table
- id (INT, primary key)
- aos_name (VARCHAR)
- description (TEXT, nullable)

### workout_pax table (junction)
- workout_id (INT, foreign key)
- pax_id (INT, foreign key)

### workout_aos table (junction)
- workout_id (INT, foreign key)
- aos_id (INT, foreign key)

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip
- MySQL database (for production)

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/f3rva/f3rva-workout-service.git
cd f3rva-workout-service
```

2. **Install dependencies:**
```bash
pip install -r requirements-dev.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run tests:**
```bash
pytest
```

5. **Start development server:**
```bash
python run_server.py
```

6. **View API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USERNAME` | MySQL username | `workout_user` |
| `DB_PASSWORD` | MySQL password | `workout_password` |
| `DB_NAME` | MySQL database name | `f3rva_workouts` |

## Testing

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file:
```bash
pytest tests/unit/test_models.py -v
```

## Code Quality

### Linting:
```bash
ruff check .
```

### Auto-fix linting issues:
```bash
ruff check --fix .
```

### Format code:
```bash
black .
```

### Type checking:
```bash
mypy app/
```

## AWS Lambda Deployment

### Using AWS CDK (example in `deployment/cdk_stack.py`):

1. **Install AWS CDK:**
```bash
npm install -g aws-cdk
```

2. **Deploy stack:**
```bash
cdk deploy
```

### Using AWS SAM:

1. **Create `template.yaml`:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  WorkoutFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: lambda_handler.lambda_handler
      Runtime: python3.11
      Environment:
        Variables:
          DB_HOST: !Ref DatabaseHost
          DB_USERNAME: !Ref DatabaseUsername
          DB_PASSWORD: !Ref DatabasePassword
          DB_NAME: !Ref DatabaseName
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: any
```

2. **Deploy:**
```bash
sam build
sam deploy --guided
```

## Production Considerations

### Security
- Use AWS Secrets Manager for database credentials
- Enable CORS configuration for your domain
- Implement authentication/authorization if needed
- Use VPC for database security

### Database
- Configure connection pooling appropriately
- Set up database monitoring and alerts
- Implement database migrations
- Regular backups

### Monitoring
- Set up CloudWatch logging and metrics
- Configure application performance monitoring
- Health check monitoring
- Error rate alerting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.
