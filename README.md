# Paystub Generator Server

A Django REST API server for generating professional paystub PDFs from templates with Stripe payment integration. This backend is designed to work seamlessly with React frontends and provides a complete solution for generating, processing, and delivering paystub documents.

## 🎯 What This Project Does

This is a **Paystub Generator Service** that allows users to:

- **Generate Professional Paystubs**: Fill PDF templates with employee data to create official-looking paystub documents
- **Process Payments Securely**: Use Stripe Checkout for secure payment processing before document delivery
- **Deliver Documents**: Send generated PDFs via email or provide direct download links
- **Support Multiple Templates**: Manage different paystub formats (W2, regular paystubs, etc.)
- **Work with React Frontends**: Full CORS support for seamless React integration

## 🚀 Key Features

- **PDF Generation**: Fill PDF templates with dynamic data using reportlab + pdfrw
- **Payment Processing**: Stripe integration for secure payments before document access
- **Email Delivery**: Send generated PDFs via email after payment completion
- **Template Management**: Upload and manage PDF templates with AcroForm fields
- **RESTful API**: Clean, documented API endpoints for frontend integration
- **React Frontend Ready**: Configured with CORS support for React applications
- **Comprehensive Testing**: Unit and integration tests with 90%+ coverage
- **Unicode Field Support**: Handles Unicode-encoded PDF form fields for international forms
- **Guest User Flow**: No authentication required - perfect for one-time document generation

## 🏗️ Architecture

```
server/
├── main/                    # Django project root
│   ├── settings.py         # Project settings with CORS configuration
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI application
├── templates/              # Django app
│   ├── models.py          # Database models (Template, TemplateInstance)
│   ├── serializers.py     # DRF serializers
│   ├── views/             # API views
│   │   ├── api.py         # Main API endpoints (ViewSets)
│   │   └── webhook.py     # Stripe webhook handler
│   ├── services/          # Business logic
│   │   ├── pdf_service.py # PDF generation using reportlab + pdfrw
│   │   ├── stripe_service.py # Stripe payment integration
│   │   └── email_service.py # Email delivery service
│   ├── utils/             # Utility functions
│   │   ├── pdf_inspector.py # PDF field inspection
│   │   └── w2_field_map.py  # W2 form field mapping
│   └── tests/             # Comprehensive test suite
│       ├── unit/          # Unit tests (including CORS tests)
│       ├── integration/   # Integration tests
│       └── fixtures/      # Test data and files
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── development/      # Development guide
│   └── deployment/       # Deployment guide
└── requirements-*.txt    # Dependencies (including django-cors-headers)
```

## 🛠️ Tech Stack

- **Backend**: Django 5.2.2, Django REST Framework
- **Database**: PostgreSQL
- **File Storage**: AWS S3
- **Payments**: Stripe Checkout
- **PDF Processing**: reportlab + pdfrw (replaced PyPDF2 for better Unicode support)
- **Email**: django-anymail
- **CORS**: django-cors-headers (React frontend support)
- **Testing**: Django Test Framework
- **Deployment**: Gunicorn, Nginx

## 🌐 React Frontend Integration

This server is specifically configured to work with React frontends:

### CORS Configuration
- **Allowed Origins**: `localhost:3000`, `127.0.0.1:3000`, `localhost:5173`, `127.0.0.1:5173`
- **Credentials**: Enabled for authentication headers and cookies
- **Methods**: All HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS)
- **Headers**: Authorization, Content-Type, and other necessary headers

Your React app can now make API calls to `http://localhost:8000/api/` without CORS issues!

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (optional, for database)
- AWS S3 bucket
- Stripe account
- Email service (SMTP)
- React frontend (optional, but supported)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd paystub-generator/server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 2. Environment Configuration

Create a `.env` file:

```env
# Database
POSTGRES_DB=paystub_generator
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
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

### 3. Database Setup

```bash
# Using Docker (recommended)
docker-compose up -d

# Or local PostgreSQL
createdb paystub_generator
python manage.py migrate
```

### 4. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### 5. Test with React Frontend

Your React app can now make API calls to `http://localhost:8000/api/` without CORS issues!

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py all
```

### Run Specific Test Categories
```bash
python run_tests.py models      # Database models
python run_tests.py services    # Business logic services
python run_tests.py views       # API views
python run_tests.py unit        # All unit tests (including CORS tests)
python run_tests.py integration # Integration tests
```

### CORS Testing
```bash
python manage.py test templates.tests.unit.test_cors
```

### Test Coverage
The project includes comprehensive tests with:
- Unit tests for all services and utilities
- Integration tests for API endpoints
- CORS configuration tests
- Mocked external services (Stripe, AWS S3, Email)
- Test fixtures and sample data

## 📚 API Documentation

### Core Endpoints

#### Templates
- `GET /api/templates/` - List all available templates
- `GET /api/templates/{id}/` - Get specific template details

#### Template Instances (Paystub Generation)
- `GET /api/template-instances/` - List instances
- `POST /api/template-instances/` - Create new paystub (initiates payment)
- `GET /api/template-instances/{id}/` - Get instance details
- `POST /api/template-instances/{id}/send-email/` - Send PDF via email (after payment)
- `GET /api/template-instances/{id}/download/` - Get download URL (after payment)

#### Webhooks
- `POST /stripe/webhook/` - Stripe payment webhook

### Example Usage

#### Create a Paystub
```bash
curl -X POST http://localhost:8000/api/template-instances/ \
  -H "Content-Type: application/json" \
  -d '{
    "template": 1,
    "data": {
      "EmployeeName": "John Doe",
      "SSN": "123-45-6789",
      "GrossPay": "5000.00",
      "NetPay": "3500.00",
      "PayPeriod": "2024-01-01 to 2024-01-15"
    }
  }'
```

#### Send PDF via Email (after payment)
```bash
curl -X POST http://localhost:8000/api/template-instances/uuid/send-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "employee@company.com"
  }'
```

For complete API documentation, see [docs/api/README.md](docs/api/README.md).

## 🔧 Development

### Project Structure

The project follows Django best practices with a clean separation of concerns:

- **Models**: Database schema for templates and instances
- **Serializers**: Data validation and transformation
- **Views**: API endpoints and request handling
- **Services**: Business logic (PDF generation, Stripe, Email)
- **Utils**: Helper functions and PDF field mapping
- **Tests**: Comprehensive test suite including CORS tests

### Adding New Features

1. **Models**: Define in `templates/models.py`
2. **Serializers**: Create in `templates/serializers.py`
3. **Views**: Add to `templates/views/api.py`
4. **Services**: Implement in `templates/services/`
5. **Tests**: Write unit and integration tests

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Follow Django naming conventions

## 🚀 Deployment

### Production Setup

1. **Server**: Ubuntu 20.04+ with Nginx
2. **Application Server**: Gunicorn
3. **Database**: PostgreSQL
4. **File Storage**: AWS S3
5. **SSL**: Let's Encrypt certificates

### Quick Deployment

```bash
# Install dependencies
pip install -r requirements-prod.txt

# Configure environment variables
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn main.wsgi:application --bind 0.0.0.0:8000
```

For detailed deployment instructions, see [docs/deployment/README.md](docs/deployment/README.md).

## 🔒 Security

- Environment variables for all secrets
- Input validation and sanitization
- CSRF protection
- Secure file upload handling
- HTTPS enforcement in production
- Rate limiting on API endpoints
- CORS configuration for authorized origins only

## 📊 Monitoring

- Application logging with rotation
- Database query monitoring
- Error tracking and alerting
- Health check endpoints
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
python run_tests.py all

# Commit changes
git add .
git commit -m "Add feature description"

# Push and create PR
git push origin feature/your-feature
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: Create an issue on GitHub
- **Development Guide**: [docs/development/README.md](docs/development/README.md)

## 🗺️ Roadmap

- [ ] User authentication and authorization
- [ ] Template versioning
- [ ] Bulk PDF generation
- [ ] Advanced PDF customization
- [ ] Analytics and reporting
- [ ] Mobile API optimization
- [ ] Webhook retry mechanism
- [ ] Caching layer (Redis)
- [ ] Rate limiting improvements
- [ ] API documentation (Swagger/OpenAPI)
- [ ] React frontend template
- [ ] Additional paystub formats 