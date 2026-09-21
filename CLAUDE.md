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

#### Pushing the PEPPOL Document Type Code List (TAPRNext pushes to Client)

```
POST /api/method/peppol_4_erpnext.peppol_4_erpnext.code_list.update_peppol_code_list
{"code_list": {"version": "9.7", "entry-count": 321, "values": [ ... ]}}

GET  /api/method/peppol_4_erpnext.peppol_4_erpnext.code_list.get_peppol_code_list_info
```

Both require the **System Manager** role. The pushed list is validated, then stored at
`<site>/private/files/peppol_4_erpnext/peppol_document_types.json`; the app-bundled copy is
the fallback for sites that were never pushed to. The sender is authoritative — the list is
always replaced, so a rollback to an older version works. The derived lookup tables are cached
beside the raw list as `peppol_document_types_index.json` and revalidated with a single `stat()`.

## Components

### DocTypes

| DocType | Type | Purpose |
|---------|------|---------|
| PEPPOL Settings | Single | Enable/disable toggle and informational text |

### Custom Fields

There is no `peppol_scheme` field. The scheme travels inside `peppol_id` itself —
`_normalise_participant_id` in `lookup.py` accepts both `0088:123` and
`iso6523-actorid-upis::0088:123`.

| DocType | Fields | Purpose |
|---------|--------|---------|
| Company | `peppol_id` | Company's PEPPOL Participant ID (sender/receiver) |
| Customer | `peppol_id` | Customer's PEPPOL Participant ID (for outbound invoices) |
| Customer | `default_invoice_format`, `invoice_format_id`, `invoice_process_id`, `default_credit_note_format`, `credit_note_format_id`, `credit_note_process_id` | Document type routing, populated from the SMP lookup by `customer.js` |
| Supplier | `peppol_id` | Supplier's PEPPOL Participant ID (for inbound invoices) |
| Sales Invoice | `send_via_peppol`, `peppol_status`, `peppol_document_name`, `peppol_sent_on`, `peppol_error`, `peppol_mlr_status`, `peppol_mlr_description` | Outbound tracking |
| Sales Invoice | `peppol_document_format`, `peppol_process_id` | Doc type + process ID copied off the Customer when the invoice is marked; read by TAPRNext |
| Purchase Invoice | `peppol_reference`, `peppol_sender_id`, `peppol_received_on`, `is_peppol_invoice` | Inbound tracking |
| Purchase Invoice | `supplier_address_line1`, `supplier_address_line2`, `supplier_city`, `supplier_state`, `supplier_postal_code`, `supplier_country`, `payment_reference`, `schedule_date` | Invoice detail pushed by TAPRNext that stock ERPNext has nowhere to put |

**These names are a wire contract, not an implementation detail.** TAPRNext posts
Purchase Invoices as a flat dict to `/api/resource/Purchase Invoice`; Frappe's
`get_valid_dict()` drops any key that is not in the doctype meta, with no error. A
field renamed or removed here becomes data that silently disappears. `tests/test_contract.py`
pins the set — the export filter in `hooks.py` must name every field in
`fixtures/custom_field.json`, or the next `bench export-fixtures` deletes the rest.

### Sales Invoice PEPPOL Status

| Status | Set by | Description |
|--------|--------|-------------|
| (empty) | — | Not marked for PEPPOL |
| Ready | This app (`mark_invoice_for_peppol`) | Marked for pickup by TAPRNext |
| Fetched | TAPRNext | Picked up; `peppol_document_name` now holds the TAPRNext document |
| Sent | TAPRNext | Sent via PEPPOL network; `peppol_sent_on` set |
| Delivered | TAPRNext | MLR received from the network; `peppol_mlr_status` set |
| Failed | TAPRNext | Delivery failed (see `peppol_error`) |

`Ready` is the only status this app sets itself; the other four arrive through
`api.update_peppol_status`. Marking requires PEPPOL Settings to be enabled — enforced
both in `can_mark_for_peppol` (for the UI) and in the `Sales Invoice` doc events in
`sales_invoice.py` (for every other write path, including the REST API).

### Key Files

```
peppol_4_erpnext/
├── hooks.py                      # App metadata, doctype_js, fixtures, before_install
├── install.py                    # Frappe/ERPNext version guard (before_install hook)
├── peppol_4_erpnext/
│   ├── api.py                    # Whitelisted API endpoints
│   ├── lookup.py                 # SMP participant lookup + doc type tables
│   ├── code_list.py              # Receives the pushed PEPPOL doc type code list
│   ├── sales_invoice.py          # Doc events: PEPPOL-enabled guard on send_via_peppol
│   ├── doctype/
│   │   └── peppol_settings/      # Settings configuration
│   └── tests/
│       └── test_contract.py      # Pins the endpoints + field names TAPRNext depends on
├── fixtures/
│   └── custom_field.json         # Custom field definitions
└── public/js/
    ├── sales_invoice.js          # "Mark for PEPPOL" button & status display
    ├── customer.js               # Doc type routing from the SMP lookup
    └── peppol_party.js           # PEPPOL ID validation on Company / Supplier
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

- frappe v15 or v16
- erpnext v15 or v16 (required for Company, Customer, Supplier, Sales/Purchase Invoice doctypes)
- Python 3.10–3.14 (a v15 bench runs 3.10–3.14, a v16 bench runs 3.14 only)
- `dnspython >= 2.0` (BDXL/NAPTR resolution in `lookup.py`) and `requests >= 2.28` (SMP queries),
  declared in `pyproject.toml` and installed by `bench get-app`

### Frappe v15 / v16

A single codebase serves both majors — there is no version branch and no compatibility
shim. Every framework API the app uses (`frappe.whitelist`, `frappe.only_for`,
`frappe.throw`, `frappe.log_error`, `frappe.get_site_path`, `frappe.get_app_path`,
`frappe.db.set_value`, `frappe.db.get_single_value`, and the client-side form APIs) has
the same signature in v15 and v16; in v16 several of them moved out of `frappe/__init__.py`
but are re-exported from it. The only real difference is the interpreter, so the code stays
within Python 3.10 syntax (`target-version = "py310"` in `pyproject.toml`).

`peppol_4_erpnext/install.py` runs as the `before_install` hook: it blocks installation on
frappe/erpnext older than v15 and warns — without blocking — past v16.
