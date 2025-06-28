Here's a **final, fully integrated backend requirement document** complete, clear, and ready:

✅ Django backend
✅ PDF templates with AcroForm fields
✅ guest payment with Stripe
✅ S3 storage
✅ email delivery after payment
✅ no authentication required

---

# 📄 **Backend Requirement Document**

## Project: Paid PDF Form Generation & Delivery Service

---

## 🧩 **Overview**

Build a Django backend that:

* Manages PDF templates (with AcroForm fields)
* Accepts JSON data to fill and generate PDFs
* Requires payment as a guest user via Stripe Checkout before download
* Stores generated documents securely in AWS S3
* Offers optional email delivery after payment
* Fully guest flow: **no user authentication**
* Supports Unicode-encoded PDF form fields

---

## 📦 **Data Model**

### Template

| Field       | Type      | Description                                   |
| ----------- | --------- | --------------------------------------------- |
| id          | UUID      | Primary key                                   |
| name        | CharField | Template name                                 |
| file        | FileField | Blank PDF with AcroForm fields (stored on S3) |
| description | TextField | Optional notes                                |
| created\_at | DateTime  | Creation timestamp                            |
| updated\_at | DateTime  | Auto-updated                                  |

---

### TemplateInstance

| Field               | Type                          | Description                  |
| ------------------- | ----------------------------- | ---------------------------- |
| id                  | UUID                          | Primary key                  |
| template            | ForeignKey → Template         | Which template was used      |
| data                | JSONField                     | JSON data submitted by user  |
| file                | FileField                     | Generated PDF (stored on S3) |
| is\_paid            | BooleanField (default: False) | True if payment completed    |
| stripe\_session\_id | CharField                     | Stripe Checkout session ID   |
| created\_at         | DateTime                      | Creation timestamp           |
| updated\_at         | DateTime                      | Auto-updated                 |

---

## 🎯 **Functional Requirements**

✅ Create and manage PDF templates (admin-only)
✅ Accept JSON data → generate filled & flattened PDF
✅ Require Stripe guest payment before download
✅ Store generated PDFs in S3 using boto3
✅ After payment, user gets:

* Direct download link
* Option to enter email to receive PDF
  ✅ Guest-only: no login/signup required
  ✅ Unicode field support for international forms

---

## 📦 **API Specification**

### `POST /api/templates/{template_id}/instances/`

Generate filled PDF & create Stripe payment session

**Request:**

```json
{
  "data": {
    "EmployeeName": "John Doe",
    "SSN": "123-45-6789",
    ...
  }
}
```

**Backend:**

* Fill PDF fields with data (using field mapping for complex forms)
* Save generated PDF to S3
* Create Stripe Checkout Session (save `stripe_session_id`)
* Save instance as unpaid

**Response:**

```json
{
  "instance_id": "uuid",
  "checkout_url": "https://checkout.stripe.com/..."
}
```

---

### `POST /api/instances/{instance_id}/send-email/`

Send the generated PDF to an email (only if paid)

**Request:**

```json
{ "email": "user@example.com" }
```

**Response:**

```json
{ "success": true }
```

---

### `GET /api/instances/{instance_id}/`

Get instance metadata

**Response:**

```json
{
  "id": "uuid",
  "template": { "id": "template_uuid", "name": "W2 Form" },
  "is_paid": true,
  "file_url": "https://s3.amazonaws.com/..."  // only if is_paid=true
}
```

---

### `GET /api/instances/{instance_id}/download/`

Direct download endpoint

* Return HTTP 403 if payment not completed

---

## 💰 **Stripe Payment Integration**

* Use Stripe Checkout for guest payments:

  * Create session per document
  * Save `stripe_session_id` in `TemplateInstance`
* Stripe webhook: `checkout.session.completed`:

  * Find instance by `stripe_session_id` or `metadata.instance_id`
  * Set `is_paid=True`

---

## 🛠 **PDF Generation Process**

1. Load PDF template (`Template.file` from S3)
2. Fill fields from JSON (using field mapping for Unicode-encoded fields)
3. Flatten PDF (make uneditable)
4. Upload generated file to S3 (`TemplateInstance.file`)

**Libraries**: `reportlab` + `pdfrw` (replaced PyPDF2 for better Unicode support)

**Field Mapping**: For complex forms like W2, use mapping dictionaries to translate business field names to PDF field names.

---

## ☁️ **Storage Configuration**

Using S3 + boto3 (`django-storages`):

```python
STORAGES = {
    'default': {'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

AWS_ACCESS_KEY_ID = ...
AWS_SECRET_ACCESS_KEY = ...
AWS_STORAGE_BUCKET_NAME = ...
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
```

Generated PDFs and templates stored in:

* `templates/`
* `templates-instances/`

---

## ✉ **Email Delivery**

After successful payment:

* User can submit email to receive:

  * S3 pre-signed download link **or**
  * PDF attached directly
* Use `django-anymail`, AWS SES, SMTP, or other service

---

## 🧪 **Validation & Business Rules**

* Validate:

  * Required JSON fields
  * Correct formats (SSN, EIN, numbers >0)
  * Email format when sending
* Prevent download until `is_paid=True`

---

## 🛡 **Security & Non-Functional Requirements**

* Validate Stripe webhook signature
* Use private S3 bucket; serve via pre-signed URLs
* Rate limiting to prevent abuse
* Logs for audit & debugging
* Reliable PDF generation & fast response

---

## ✅ **User Flow (guest)**

1️⃣ User fills JSON data & requests document
2️⃣ Backend:

* Generates PDF
* Starts Stripe checkout
  3️⃣ User pays via Stripe
  4️⃣ Stripe webhook updates `is_paid=True`
  5️⃣ Backend returns:
* Direct download link (from S3)
* User can enter email to receive PDF

---

## ⚙ **Tech Stack**

* Django + DRF
* Stripe Python SDK
* boto3 + django-storages
* `reportlab` + `pdfrw` for PDFs
* Mail: `django-anymail` or similar

---

## 📌 **Future Enhancements**

* Download expiration / single-use links
* Batch fill & pay for multiple documents
* Dynamic pricing per template
* Discount & promo codes

