# Development Guide

## Overview
This guide covers setting up the development environment, running tests, and contributing to the Paystub Generator project. The project is designed to work with React frontends with full CORS support.

## Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (optional, for database)
- Git
- Node.js (optional, for React frontend development)

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

**Note**: The project uses **reportlab + pdfrw** for PDF processing (replaced PyPDF2 for better Unicode field support) and **django-cors-headers** for React frontend integration.

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

## Frontend Integration

### CORS Configuration
The Django server is configured with CORS support for React frontends:

#### Allowed Origins
- `http://localhost:3000` (Create React App)
- `http://127.0.0.1:3000` (Alternative localhost)
- `http://localhost:5173` (Vite)
- `http://127.0.0.1:5173` (Vite alternative)

#### Configuration Details
- **Credentials**: Enabled for authentication headers and cookies
- **Methods**: All HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS)
- **Headers**: Authorization, Content-Type, and other necessary headers

### React Frontend Development

#### Setting Up React Frontend
```bash
# Create React app (if not already created)
npx create-react-app paystub-frontend
cd paystub-frontend

# Or use Vite
npm create vite@latest paystub-frontend -- --template react
cd paystub-frontend
```

Your React frontend can now make API calls to the Django server without CORS issues.

#### Testing CORS Configuration
```bash
# Test CORS headers
python manage.py test templates.tests.unit.test_cors
```

### Adding New Origins
To add new origins for your React frontend:

1. Edit `main/settings.py`
2. Add to `CORS_ALLOWED_ORIGINS`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://your-custom-domain.com",  # Add your domain
]
```

## PDF Processing

### Overview
The application uses **reportlab + pdfrw** for PDF generation and form field filling. This combination provides:

- **Better Unicode support** for international characters
- **Improved field detection** for complex PDF forms
- **More reliable PDF processing** than PyPDF2

### PDF Field Mapping
For complex forms like W2, the application includes field mapping utilities:

- **`templates/utils/pdf_inspector.py`**: Inspects PDF form fields
- **`templates/utils/w2_field_map.py`**: Maps business field names to PDF field names

### Working with PDF Templates

#### 1. Inspecting PDF Fields
```python
from templates.utils.pdf_inspector import PDFInspector

# Inspect form fields in a PDF
fields = PDFInspector.inspect_form_fields(pdf_file)
print(fields)
```

#### 2. Creating Field Mappings
For forms with Unicode-encoded field names (like `<FEFF00630031005F0031005B0030005D>`), create mappings in `w2_field_map.py`:

```python
FIELD_MAP = {
    'employee_ssn': 'f1_01[0]',
    'employee_ein': 'f1_02[0]',
    # ... more mappings
}
```

#### 3. Testing PDF Generation
```bash
# Run W2 PDF tests
python run_tests.py w2

# Run all PDF-related tests
python run_tests.py services
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
python run_tests.py w2        # W2 PDF generation tests
python run_tests.py unit      # All unit tests (including CORS tests)

# Run specific test file
python run_tests.py templates.tests.unit.test_api_views

# Test CORS configuration
python manage.py test templates.tests.unit.test_cors
```

### Test Structure
```
templates/tests/
├── unit/           # Unit tests for individual components
│   ├── test_cors.py # CORS configuration tests
│   └── ...         # Other unit tests
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

#### CORS Tests
- Test CORS headers are present
- Verify preflight OPTIONS requests
- Test multiple origins
- Ensure disallowed origins are rejected

#### PDF Tests
- Test PDF generation with real templates
- Verify field filling accuracy
- Test Unicode field name handling

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

### Frontend Integration
- Use consistent API endpoint patterns
- Handle CORS errors gracefully
- Implement proper error handling for API calls

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