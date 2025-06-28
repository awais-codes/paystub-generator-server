# API Documentation

## Overview
The Paystub Generator API provides endpoints for managing templates, generating PDFs, and handling payments through Stripe. The system uses **reportlab + pdfrw** for PDF processing with support for Unicode-encoded form fields.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Currently, the API does not require authentication. In production, consider implementing JWT or API key authentication.

## PDF Processing Features

### Unicode Field Support
The API supports PDF forms with Unicode-encoded field names (e.g., `<FEFF00630031005F0031005B0030005D>` → `c1_1[0]`). This is particularly useful for:
- International forms (W2, 1099, etc.)
- Forms with special characters
- Complex multi-page documents

### Field Mapping
For complex forms, the system uses field mapping to translate business field names to PDF field names:

```json
{
  "employee_ssn": "123-45-6789",      // Maps to f1_01[0] in PDF
  "employee_ein": "12-3456789",       // Maps to f1_02[0] in PDF
  "wages_tips": "50000.00"           // Maps to f1_09[0] in PDF
}
```

### Supported Form Types
- **W2 Forms**: Complete field mapping available
- **Paystubs**: Standard field support
- **Custom Forms**: Auto-detection of form fields

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
      "SSN": "123-45-6789",
      "GrossPay": "5000.00",
      "NetPay": "3500.00"
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

### Creating a W2 Template Instance

```bash
curl -X POST http://localhost:8000/api/template-instances/ \
  -H "Content-Type: application/json" \
  -d '{
    "template": 1,
    "data": {
      "employee_ssn": "123-45-6789",
      "employee_ein": "12-3456789",
      "employer_name_address_zip": "ACME Corp, 123 Business Ave, NY 10001",
      "control_number": "2024001",
      "firt_name_and_initial": "John A",
      "last_name": "Smith",
      "wages_tips": "75000.00",
      "fed_income_tax_withheld": "15000.00",
      "social_security_wages": "75000.00",
      "social_security_wages_withheld": "4650.00",
      "medicare_wages": "75000.00",
      "medicare_tax_witheld": "1087.50"
    }
  }'
```

### Creating a Paystub Template Instance

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