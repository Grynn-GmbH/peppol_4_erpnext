# PEPPOL 4 ERPNext - Architecture Documentation

## Overview

This is an ERPNext extension app that integrates with TAPRNext (a PEPPOL access point) for e-invoice exchange. It is installed on client ERPNext sites to enable sending and receiving of PEPPOL e-invoices.

## Architecture

**Key Principle:** TAPRNext initiates all communication. The client ERPNext does not need to store TAPRNext credentials.

### Sending Sales Invoices (Outbound)

```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│  Client ERPNext     │         │  TAPRNext            │         │  PEPPOL Network │
│  + peppol_4_erpnext │ ◄────── │  xxx.gc.tapr.ch      │ ──────► │  (Recipient)    │
│                     │  PULL   │  (PEPPOL Access Pt)  │         │                 │
└─────────────────────┘         └──────────────────────┘         └─────────────────┘

Flow:
1. User submits Sales Invoice in ERPNext
2. User checks "Send via PEPPOL" checkbox (or clicks "Mark for PEPPOL" button)
3. Invoice status set to "Ready"
4. TAPRNext batch job fetches invoices with send_via_peppol=1 and peppol_status="Ready"
5. TAPRNext delivers via PEPPOL network to recipient
6. TAPRNext updates invoice status and MLR response fields
```

### Receiving Purchase Invoices (Inbound)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────────┐
│  PEPPOL Network │ ──────► │  TAPRNext        │ ──────► │  Client ERPNext     │
│  (Sender)       │         │  xxx.gc.tapr.ch  │  PUSH   │  + peppol_4_erpnext │
└─────────────────┘         │                  │ ──────► │                     │
                            │  User approves   │         └─────────────────────┘
                            │  Batch job sends │
                            └──────────────────┘

Flow:
1. TAPRNext receives Purchase Invoice from PEPPOL network
2. User reviews and approves invoice in TAPRNext
3. TAPRNext batch job creates Purchase Invoice in client ERPNext
4. TAPRNext calls POST /api/resource/Purchase Invoice with ERPNext native format
5. Purchase Invoice created in ERPNext (as Draft)
```

**Note:** TAPRNext stores the client ERPNext API credentials (api_key, api_secret) - not the other way around.

## TAPRNext API

TAPRNext is a Frappe-based application using standard Frappe REST API patterns.

### Authentication

TAPRNext authenticates to client ERPNext using:
```
Authorization: token api_key:api_secret
```

### Endpoints Used by TAPRNext

#### Fetching Sales Invoices (TAPRNext pulls from Client)

```
GET /api/resource/Sales Invoice?filters=[["send_via_peppol","=",1],["peppol_status","=","Ready"]]
```

#### Updating Sales Invoice Status (TAPRNext updates Client)

```
PUT /api/resource/Sales Invoice/{name}
{
  "peppol_status": "Sent",
  "peppol_document_name": "SINV-TAPR-00001",
  "peppol_sent_on": "2024-01-15 10:30:00",
  "peppol_mlr_status": "Accepted",
  "peppol_mlr_description": "Message delivered successfully"
}
```

#### Creating Purchase Invoices (TAPRNext pushes to Client)

```
POST /api/resource/Purchase Invoice
```

TAPRNext sends the invoice in ERPNext's native Purchase Invoice format, including PEPPOL tracking fields.

## Components

### DocTypes

| DocType | Type | Purpose |
|---------|------|---------|
| PEPPOL Settings | Single | Enable/disable toggle and informational text |

### Custom Fields

| DocType | Fields | Purpose |
|---------|--------|---------|
| Company | `peppol_id`, `peppol_scheme` | Company's PEPPOL Participant ID (sender/receiver) |
| Customer | `peppol_id`, `peppol_scheme` | Customer's PEPPOL Participant ID (for outbound invoices) |
| Supplier | `peppol_id`, `peppol_scheme` | Supplier's PEPPOL Participant ID (for inbound invoices) |
| Sales Invoice | `send_via_peppol`, `peppol_status`, `peppol_document_name`, `peppol_sent_on`, `peppol_error`, `peppol_mlr_status`, `peppol_mlr_description` | Outbound tracking |
| Purchase Invoice | `peppol_reference`, `peppol_sender_id`, `peppol_received_on`, `is_peppol_invoice` | Inbound tracking |

### Sales Invoice PEPPOL Status

| Status | Description |
|--------|-------------|
| (empty) | Not marked for PEPPOL |
| Ready | Marked for pickup by TAPRNext |
| Sent | Picked up and sent via PEPPOL network |
| Delivered | Confirmed delivered to recipient |
| Failed | Delivery failed (see error message) |

### Key Files

```
peppol_4_erpnext/
├── peppol_4_erpnext/
│   ├── api.py                    # Whitelisted API endpoints
│   ├── doctype/
│   │   └── peppol_settings/      # Settings configuration
│   └── fixtures/
│       └── custom_field.json     # Custom field definitions
└── public/js/
    └── sales_invoice.js          # "Mark for PEPPOL" button & status display
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

## Message Level Response (MLR)

The MLR fields on Sales Invoice track the AS4 network delivery status:

- `peppol_mlr_status`: Status code from the AS4 network (e.g., "Accepted", "Rejected")
- `peppol_mlr_description`: Detailed description of the delivery result

These fields are populated by TAPRNext after attempting delivery via the PEPPOL network.

## Dependencies

- frappe >= 15.0
- erpnext >= 15.0 (required for Company, Customer, Supplier, Sales/Purchase Invoice doctypes)
