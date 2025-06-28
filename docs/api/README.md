# API Documentation

## Overview
The Paystub Generator API provides endpoints for managing templates, generating PDFs, and handling payments through Stripe.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Currently, the API does not require authentication. In production, consider implementing JWT or API key authentication.

## Endpoints

### Templates

#### List Templates
- **GET** `/templates/`
- **Description**: Retrieve all available templates
- **Response**: List of template objects

#### Create Template
- **POST** `/templates/`
- **Description**: Create a new template
- **Content-Type**: `multipart/form-data`
- **Body**:
  ```json
  {
    "name": "Template Name",
    "description": "Template Description",
    "file": "PDF file"
  }
  ```

#### Retrieve Template
- **GET** `/templates/{id}/`
- **Description**: Get a specific template by ID

#### Update Template
- **PUT** `/templates/{id}/`
- **Description**: Update an existing template

#### Delete Template
- **DELETE** `/templates/{id}/`
- **Description**: Delete a template

### Template Instances

#### List Instances
- **GET** `/template-instances/`
- **Description**: Retrieve all template instances

#### Create Instance
- **POST** `/template-instances/`
- **Description**: Create a new template instance and initiate payment
- **Body**:
  ```json
  {
    "template": 1,
    "data": {
      "EmployeeName": "John Doe",
      "SSN": "123-45-6789"
    }
  }
  ```
- **Response**:
  ```json
  {
    "instance_id": "uuid",
    "checkout_url": "https://checkout.stripe.com/...",
    "message": "Payment required"
  }
  ```

#### Retrieve Instance
- **GET** `/template-instances/{id}/`
- **Description**: Get a specific template instance

#### Send Email
- **POST** `/template-instances/{id}/send-email/`
- **Description**: Send PDF via email (requires payment)
- **Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```

#### Download PDF
- **GET** `/template-instances/{id}/download/`
- **Description**: Get download URL for PDF (requires payment)

### Webhooks

#### Stripe Webhook
- **POST** `/stripe/webhook/`
- **Description**: Handle Stripe payment confirmations
- **Headers**: `Stripe-Signature` required
- **Body**: Raw webhook payload from Stripe

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `403` - Forbidden (payment required)
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a JSON object with an `error` field:

```json
{
  "error": "Error message description"
}
```

## Example Usage

### Creating a Template Instance

```bash
curl -X POST http://localhost:8000/api/template-instances/ \
  -H "Content-Type: application/json" \
  -d '{
    "template": 1,
    "data": {
      "EmployeeName": "Jane Smith",
      "SSN": "987-65-4321",
      "GrossPay": "5000.00",
      "NetPay": "3500.00"
    }
  }'
```

### Sending PDF via Email

```bash
curl -X POST http://localhost:8000/api/template-instances/uuid/send-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
``` 