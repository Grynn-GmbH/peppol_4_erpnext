# Overview & Prerequisites

## What is PEPPOL?

PEPPOL (Pan-European Public Procurement Online) is a standardized network for exchanging electronic business documents, primarily e-invoices, between organizations across Europe and beyond.

## What Does This Integration Do?

The `peppol_4_erpnext` app connects your ERPNext instance to the PEPPOL network via TAPRNext, enabling you to:

- **Send** Sales Invoices to customers on the PEPPOL network
- **Receive** Purchase Invoices from suppliers on the PEPPOL network

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│  Your ERPNext       │         │  TAPRNext            │         │  PEPPOL Network │
│  + peppol_4_erpnext │ ◄─────► │  (Access Point)      │ ◄─────► │  (Partners)     │
└─────────────────────┘         └──────────────────────┘         └─────────────────┘
```

**Key principle:** TAPRNext initiates all communication. Your ERPNext instance does not need to store TAPRNext credentials.

### Sending Flow
1. You submit a Sales Invoice in ERPNext
2. You mark it for PEPPOL delivery
3. TAPRNext fetches the invoice
4. TAPRNext delivers it via PEPPOL
5. TAPRNext updates the status in ERPNext

### Receiving Flow
1. TAPRNext receives invoice from PEPPOL
2. You review and approve in TAPRNext
3. TAPRNext creates Purchase Invoice in ERPNext

## Prerequisites

Before starting, ensure you have:

| Requirement | Details |
|-------------|---------|
| ERPNext v15+ | This app requires ERPNext version 15 or higher |
| TAPRNext Account | Sign up at [cloud.tapr.ch](https://cloud.tapr.ch/dashboard/signup?product=inflow) |
| PEPPOL Registration | Completed through TAPRNext onboarding |
| PEPPOL Participant ID | Assigned after registration |

## Next Steps

- [Installation Guide](02-installation.md)
