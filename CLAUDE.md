# PEPPOL 4 ERPNext - Architecture Documentation

## Overview

This is an ERPNext extension app that integrates with TAPRNext (a PEPPOL access point) for e-invoice exchange. It is installed on client ERPNext sites to enable sending and receiving of PEPPOL e-invoices.

## Architecture

### Sending Sales Invoices (Outbound)

```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│  Client ERPNext     │         │  TAPRNext            │         │  PEPPOL Network │
│  + peppol_4_erpnext │ ──────► │  xxx.gc.tapr.ch      │ ──────► │  (Recipient)    │
│                     │   API   │  (PEPPOL Access Pt)  │         │                 │
└─────────────────────┘         └──────────────────────┘         └─────────────────┘

Flow:
1. User submits Sales Invoice in ERPNext
2. User clicks "Send to PEPPOL" button
3. peppol_4_erpnext maps ERPNext Sales Invoice to TAPRNext format
4. POST to TAPRNext API: /api/resource/Sales Invoice
5. TAPRNext delivers via PEPPOL network to recipient
```

### Receiving Purchase Invoices (Inbound)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────────┐
│  PEPPOL Network │ ──────► │  TAPRNext        │ ──────► │  Client ERPNext     │
│  (Sender)       │         │  xxx.gc.tapr.ch  │  POST   │  + peppol_4_erpnext │
└─────────────────┘         │                  │ ──────► │  API endpoint       │
                            │  User approves   │         │                     │
                            │  Batch job sends │         └─────────────────────┘
                            └──────────────────┘

Flow:
1. TAPRNext receives Purchase Invoice from PEPPOL network
2. User reviews and approves invoice in TAPRNext
3. TAPRNext batch job sends approved invoice to client ERPNext
4. peppol_4_erpnext receives POST request with invoice data
5. peppol_4_erpnext maps TAPRNext format to ERPNext Purchase Invoice
6. Purchase Invoice created in ERPNext (as Draft)
```

**Note:** TAPRNext pushes invoices to ERPNext - there is no polling. The client configures their ERPNext API credentials (api_key, api_secret) in TAPRNext.

## TAPRNext API

TAPRNext is a Frappe-based application using standard Frappe REST API patterns.

### Authentication

```
Authorization: token api_key:api_secret
```

### Endpoints Used

#### Sending Sales Invoices (Client → TAPRNext)

```
POST /api/resource/Sales Invoice
```

#### Receiving Purchase Invoices (TAPRNext → Client)

TAPRNext calls the standard ERPNext Purchase Invoice API directly:

```
POST /api/resource/Purchase Invoice
```

TAPRNext handles the mapping to ERPNext's native Purchase Invoice format. It also populates the PEPPOL tracking fields (`peppol_reference`, `peppol_sender_id`, `peppol_received_on`, `is_peppol_invoice`).

### Invoice Payload Structure

Both Sales Invoice and Purchase Invoice use the same structure (e-invoices are standardized):

```json
{
  "legal_entity": "Company ABC",
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "vendor_name": "Acme Corp",
  "vendor_vat_number": "DE123456789",
  "currency": "EUR",
  "net_total": 1000.00,
  "tax_total": 190.00,
  "grand_total": 1190.00,
  "items": [
    {
      "item_description": "Widget A",
      "quantity": 10,
      "unit_price": 100.00,
      "net_amount": 1000.00,
      "tax_rate": 19,
      "tax_amount": 190.00
    }
  ]
}
```

## Components

### DocTypes

| DocType | Type | Purpose |
|---------|------|---------|
| PEPPOL Settings | Single | TAPRNext URL, API Key, API Secret, defaults |

### Custom Fields

| DocType | Fields | Purpose |
|---------|--------|---------|
| Company | `peppol_id`, `peppol_scheme` | Sender PEPPOL ID |
| Customer | `peppol_id`, `peppol_scheme` | Receiver PEPPOL ID (for Sales) |
| Supplier | `peppol_id`, `peppol_scheme` | Sender PEPPOL ID (for Purchase) |
| Sales Invoice | `peppol_status`, `peppol_document_name`, `peppol_sent_on`, `peppol_error` | Outbound tracking |
| Purchase Invoice | `peppol_reference`, `peppol_sender_id`, `peppol_received_on`, `is_peppol_invoice` | Inbound tracking |

### Key Files

```
peppol_4_erpnext/
├── peppol_4_erpnext/
│   ├── api.py                    # Whitelisted API endpoints
│   ├── taprnext_client.py        # HTTP client for TAPRNext
│   ├── invoice_mapper.py         # ERPNext ↔ TAPRNext mapping
│   ├── doctype/
│   │   └── peppol_settings/      # Settings configuration
│   └── fixtures/
│       └── custom_field.json     # Custom field definitions
└── public/js/
    └── sales_invoice.js          # "Send to PEPPOL" button
```

## PEPPOL ID Schemes

Common scheme identifiers:

| Code | Description |
|------|-------------|
| 0007:SE:ORGNR | Swedish Organization Number |
| 0088:EAN/GLN | EAN Location Code (GLN) |
| 0106:NL:KVK | Netherlands KvK Number |
| 0190:NL:OINO | Netherlands OINO |
| 9914:PEPPOL | PEPPOL Participant ID |
| 9915:AT:VAT | Austrian VAT Number |
| 9959:CH:UID | Swiss UID |

## Dependencies

- frappe >= 15.0
- erpnext >= 15.0 (required for Company, Customer, Supplier, Sales/Purchase Invoice doctypes)
