# Supplier Setup

Configure suppliers to receive and match incoming PEPPOL invoices.

## Why Add PEPPOL IDs to Suppliers?

When TAPRNext receives an invoice from the PEPPOL network, it needs to match the sender to a Supplier in your ERPNext. Adding PEPPOL IDs to suppliers enables automatic matching.

## Add PEPPOL ID to Supplier

1. Go to **Supplier** in ERPNext
2. Open the supplier record
3. Scroll to the **PEPPOL** section
4. Enter their **PEPPOL Participant ID**
5. Select the correct **PEPPOL ID Scheme**
6. Save

<!-- Screenshot: Supplier PEPPOL section -->

## Finding a Supplier's PEPPOL ID

### From Received Invoices

If you've already received a PEPPOL invoice from this supplier:

1. Open the Purchase Invoice
2. Check the **Sender PEPPOL ID** field
3. Copy this to the Supplier record

### From Their Documents

Look for the PEPPOL ID on:
- Their invoices or quotes
- Company letterhead
- Ask their accounts department

### PEPPOL Directory

Search [directory.peppol.eu](https://directory.peppol.eu/) for the supplier.

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

## New Suppliers from PEPPOL

When you receive an invoice from a new sender:

1. TAPRNext creates the Purchase Invoice
2. The **Sender PEPPOL ID** is recorded
3. You may need to create a new Supplier in ERPNext
4. Match the Supplier to the invoice
5. Add the PEPPOL ID to the Supplier for future matching

## Next Steps

- [Receiving Invoices](07-receiving-invoices.md) - Handle incoming PEPPOL invoices
