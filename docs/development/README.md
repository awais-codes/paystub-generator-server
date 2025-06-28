# Development Guide

## Overview
This guide covers setting up the development environment, running tests, and contributing to the Paystub Generator project.

## Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (optional, for database)
- Git

## Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd paystub-generator/server
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### 4. Environment Variables
Create a `.env` file in the project root:

```env
# Database
POSTGRES_DB=paystub_generator
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (for sending PDFs)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True

# Django
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup

#### Option A: Using Docker (Recommended)
```bash
docker-compose up -d
```

#### Option B: Local PostgreSQL
```bash
# Create database
createdb paystub_generator

# Run migrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

## Testing

### Running Tests
```bash
# Run all tests
python run_tests.py all

# Run specific test categories
python run_tests.py models
python run_tests.py services
python run_tests.py views

# Run specific test file
python run_tests.py templates.tests.unit.test_api_views
```

### Test Structure
```
templates/tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for complete workflows
└── fixtures/       # Test data and files
```

### Writing Tests

#### Unit Tests
- Test individual functions and methods
- Use mocking for external dependencies
- Keep tests focused and fast

#### Integration Tests
- Test complete workflows
- Use real database and file operations
- Test API endpoints end-to-end

#### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `<ClassName>TestCase`
- Test methods: `test_<description>`

## Code Style

### Python
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 88 characters (Black formatter)

### Django
- Use Django's built-in conventions
- Follow Django REST Framework patterns
- Use meaningful model field names

### File Organization
```
templates/
├── models.py           # Database models
├── serializers.py      # DRF serializers
├── admin.py           # Django admin
├── views/             # API views
│   ├── api.py         # Main API endpoints
│   └── webhook.py     # Stripe webhook handler
├── services/          # Business logic
│   ├── pdf_service.py
│   ├── stripe_service.py
│   └── email_service.py
├── utils/             # Utility functions
└── tests/             # Test files
```

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write code following the style guide
- Add tests for new functionality
- Update documentation if needed

### 3. Run Tests
```bash
python run_tests.py all
```

### 4. Commit Changes
```bash
git add .
git commit -m "Add feature description"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## Common Tasks

### Adding a New Model
1. Define the model in `models.py`
2. Create and run migrations
3. Add to admin interface
4. Create serializer
5. Add API views
6. Write tests

### Adding a New API Endpoint
1. Add view to `views/api.py`
2. Update URL configuration
3. Add serializer if needed
4. Write tests
5. Update API documentation

### Adding a New Service
1. Create service file in `services/`
2. Implement business logic
3. Add error handling
4. Write unit tests
5. Update integration tests

## Debugging

### Django Debug Toolbar
Add to `settings.py` for development:
```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### Logging
Configure logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## Performance

### Database Optimization
- Use `select_related()` and `prefetch_related()` for related objects
- Add database indexes for frequently queried fields
- Monitor slow queries

### File Storage
- Use S3 for production file storage
- Implement file cleanup for temporary files
- Consider CDN for static files

## Security

### Environment Variables
- Never commit sensitive data to version control
- Use environment variables for all secrets
- Rotate keys regularly

### Input Validation
- Validate all user inputs
- Use Django forms and serializers
- Sanitize file uploads

### Authentication
- Implement proper authentication for production
- Use HTTPS in production
- Consider rate limiting

## Deployment

See the [Deployment Guide](../deployment/README.md) for production deployment instructions. 