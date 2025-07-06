# API Documentation

## Overview
The Paystub Generator API provides endpoints for managing templates, generating PDFs, and handling payments through Stripe. The system uses **reportlab + pdfrw** for PDF processing with support for Unicode-encoded form fields. This API is designed to work seamlessly with React frontends with full CORS support.

## Base URL
```
http://localhost:8000/api/
```

## Frontend Integration

### CORS Configuration
This API is configured with CORS support for React frontends:

- **Allowed Origins**: 
  - `http://localhost:3000` (Create React App)
  - `http://127.0.0.1:3000` (Alternative localhost)
  - `http://localhost:5173` (Vite)
  - `http://127.0.0.1:5173` (Vite alternative)
- **Credentials**: Enabled for authentication headers and cookies
- **Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS
- **Headers**: Authorization, Content-Type, and other necessary headers

Your React frontend can make API calls to this server without CORS issues.

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

## New Preview-Based Workflow (Recommended)

### Flow
1. **Create Preview**: User submits form data to generate a preview PDF using the template's `preview_file`.
2. **Update Preview**: User can update the preview with new data (regenerates the preview PDF).
3. **Create Instance from Preview**: When satisfied, user creates a final template instance from the preview (using the main template file), which initiates payment. **After instance creation, the preview is automatically deleted.**

### Endpoints

#### Create Preview
- **POST** `/template-previews/`
- **Description**: Generate a preview PDF using the template's preview file and user data.
- **Body**:
  ```json
  {
    "template": "template-uuid",
    "data": {
      "employee_ssn": "123-45-6789",
      "wages_tips": "50000"
    }
  }
  ```
- **Response**:
  ```json
  {
    "id": "preview-uuid",
    "file_url": "https://.../template-previews/preview-uuid.pdf",
    ...
  }
  ```

#### Update Preview
- **PATCH** `/template-previews/{id}/`
- **Description**: Update the preview with new data and regenerate the preview PDF.
- **Body**:
  ```json
  {
    "data": {
      "employee_ssn": "987-65-4321",
      "wages_tips": "60000"
    }
  }
  ```
- **Response**: Same as create.

#### Create Instance from Preview
- **POST** `/template-instances/`
- **Description**: Create a final template instance from a preview (uses the main template file, not the preview file). **The preview is deleted after instance creation.**
- **Body**:
  ```json
  {
    "preview_id": "preview-uuid"
  }
  ```
- **Response**:
  ```json
  {
    "instance_id": "instance-uuid",
    "checkout_url": "https://checkout.stripe.com/...",
    "message": "PDF generated successfully. Please complete payment to download."
  }
  ```

## Legacy Flow (Direct Instance Creation)

(Still supported, but preview-based flow is recommended for best UX.)

#### Create Instance
- **POST** `/template-instances/`
- **Description**: Create a new template instance and initiate payment
- **Body**:
  ```json
  {
    "template": "template-uuid",
    "data": {
      "employee_ssn": "123-45-6789",
      ...
    }
  }
  ```
- **Response**: Same as above.

## Endpoints

### Templates

#### List Templates
- **GET** `/templates/`
- **Description**: Retrieve all available templates
- **Response**: List of template objects
- **CORS**: ✅ Supported

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
- **CORS**: ✅ Supported

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
- **CORS**: ✅ Supported

#### Send Email
- **POST** `/template-instances/{id}/send-email/`
- **Description**: Send PDF via email (requires payment)
- **CORS**: ✅ Supported
- **Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```

#### Download PDF
- **GET** `/template-instances/{id}/download/`
- **Description**: Get download URL for PDF (requires payment)
- **CORS**: ✅ Supported

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

### Preview Workflow Example

```bash
# 1. Create a preview
curl -X POST http://localhost:8000/api/template-previews/ \
  -H "Content-Type: application/json" \
  -d '{
    "template": "TEMPLATE_UUID",
    "data": {"employee_ssn": "123-45-6789", "wages_tips": "50000"}
  }'

# 2. Update the preview
curl -X PATCH http://localhost:8000/api/template-previews/PREVIEW_UUID/ \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"employee_ssn": "987-65-4321", "wages_tips": "60000"}
  }'

# 3. Create an instance from the preview
curl -X POST http://localhost:8000/api/template-instances/ \
  -H "Content-Type: application/json" \
  -d '{
    "preview_id": "PREVIEW_UUID"
  }'
```

## Testing CORS Configuration

To test that CORS is working correctly with your React frontend:

```bash
# Test CORS headers
python manage.py test templates.tests.unit.test_cors
```

This will verify that:
- CORS headers are present in responses
- Preflight OPTIONS requests work correctly
- Credentials are allowed
- Multiple origins are supported
- Disallowed origins are properly rejected 