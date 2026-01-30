# Customer Setup

Add PEPPOL IDs to customers to enable sending e-invoices.

## Finding a Customer's PEPPOL ID

### PEPPOL Directory Lookup

Search the PEPPOL network to find if your customer is registered:

1. Go to [directory.peppol.eu](https://directory.peppol.eu/)
2. Search by company name or identifier
3. Note their **Participant ID** and **Scheme**

### Ask Your Customer

If not found in the directory, ask your customer directly for:
- Their PEPPOL Participant ID
- The scheme they use (see [Company Setup](03-company-setup.md) for scheme list)

## Add PEPPOL ID to Customer in ERPNext

1. Go to **Customer** in ERPNext
2. Open the customer record
3. Scroll to the **PEPPOL** section
4. Enter their **PEPPOL Participant ID**
5. Select the correct **PEPPOL ID Scheme**
6. Save

<!-- Screenshot: Customer PEPPOL section -->

## PEPPOL Schemes Reference

| Code | Country | Identifier |
|------|---------|------------|
| `0007:SE:ORGNR` | Sweden | Organization Number |
| `0088:EAN/GLN` | International | GLN Code |
| `0106:NL:KVK` | Netherlands | KvK Number |
| `0190:NL:OINO` | Netherlands | OINO |
| `0199:LEI` | International | Legal Entity Identifier |
| `9914:PEPPOL` | International | Generic PEPPOL |
| `9915:AT:VAT` | Austria | VAT Number |
| `9959:CH:UID` | Switzerland | UID |

## What If a Customer Doesn't Have a PEPPOL ID?

If your customer is not registered on the PEPPOL network:

- You cannot send them e-invoices via PEPPOL
- Use traditional invoicing methods (email, PDF, postal)
- Encourage them to register with a PEPPOL access point

## Bulk Update

For many customers, you can use Data Import:

1. Export your Customer list
2. Add `peppol_id` and `peppol_scheme` columns
3. Fill in the values
4. Import back into ERPNext

## Next Steps

- [Sending Invoices](05-sending-invoices.md) - Send your first PEPPOL invoice
