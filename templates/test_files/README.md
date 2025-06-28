# Test PDF Files

This directory contains test PDF files for testing the PDF generation service.

## Adding Test PDF Files

1. **Create your test PDF templates** with form fields that match your expected data structure
2. **Name your files** descriptively (e.g., `paystub_template.pdf`, `w2_template.pdf`)
3. **Add form fields** with names that match your test data:
   - `EmployeeName`
   - `SSN`
   - `GrossPay`
   - `NetPay`
   - `PayPeriod`
   - `PayDate`

## Recommended Test Files

- `paystub_template.pdf` - Basic paystub template
- `w2_template.pdf` - W2 form template
- `1099_template.pdf` - 1099 form template

## Form Field Requirements

Your PDF templates should have AcroForm fields with the following names:
- Employee information fields
- Pay information fields
- Date fields
- Any other fields you want to populate

## Testing

The tests will automatically detect and use these files if they exist. If files are not found, the tests will be skipped, so they won't break your CI/CD pipeline.

## Example Form Field Names

```
EmployeeName
SSN
GrossPay
NetPay
PayPeriod
PayDate
EmployerName
EmployerEIN
```

## Creating Test PDFs

You can create test PDFs using:
- Adobe Acrobat
- PDF form builders
- Online PDF form creators
- Or use the utility functions in `tests.py` to generate simple test PDFs 