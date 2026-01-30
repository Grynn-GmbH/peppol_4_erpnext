# Quick Start Guide

Get up and running with PEPPOL e-invoicing in 5 minutes.

## Checklist

### 1. Sign Up for TAPRNext
- Go to [cloud.tapr.ch/dashboard/signup](https://cloud.tapr.ch/dashboard/signup?product=inflow)
- Complete registration and PEPPOL onboarding
- Note your assigned PEPPOL Participant ID

### 2. Install the App
```bash
bench get-app https://github.com/[repo]/peppol_4_erpnext
bench --site your-site install-app peppol_4_erpnext
```

### 3. Configure ERPNext
- **PEPPOL Settings**: Enable PEPPOL integration
- **Company**: Add your PEPPOL ID and scheme
- **Customers**: Add PEPPOL IDs for customers you'll invoice

### 4. Connect TAPRNext to ERPNext
- In TAPRNext dashboard, add your ERPNext API credentials
- Test the connection

### 5. Send Your First Invoice
1. Create and submit a Sales Invoice
2. Click **Mark for PEPPOL**
3. Status changes to "Ready"
4. TAPRNext picks up and delivers the invoice

## What's Next?

- [Overview & Prerequisites](01-overview-prerequisites.md) - Understand the architecture
- [Installation Guide](02-installation.md) - Detailed setup instructions
- [Company Setup](03-company-setup.md) - Configure your PEPPOL identity
- [Sending Invoices](05-sending-invoices.md) - Complete sending workflow
- [Receiving Invoices](07-receiving-invoices.md) - Handle incoming invoices
