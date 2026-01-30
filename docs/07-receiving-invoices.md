# Receiving Purchase Invoices

Receive e-invoices from suppliers via the PEPPOL network.

## Prerequisites

To receive PEPPOL invoices:
- [x] TAPRNext account is active
- [x] Your Company has a registered PEPPOL ID
- [x] TAPRNext has your ERPNext API credentials
- [x] Suppliers exist in ERPNext (recommended)

## How Invoices Arrive

```
Supplier → PEPPOL Network → TAPRNext → ERPNext
```

1. A supplier sends an invoice to your PEPPOL ID
2. TAPRNext receives it from the PEPPOL network
3. You review and approve in TAPRNext
4. TAPRNext creates a Purchase Invoice in ERPNext

## Step 1: Review in TAPRNext

When an invoice arrives:

1. Log in to TAPRNext dashboard
2. Go to **Inbound Documents**
3. Review the invoice details
4. Verify the sender and amounts
5. Click **Approve**

<!-- Screenshot: TAPRNext inbound review -->

## Step 2: Push to ERPNext

After approval:

1. TAPRNext batch job processes approved invoices
2. Creates Purchase Invoice in your ERPNext
3. Invoice appears as **Draft** status

This happens automatically after approval.

## Step 3: Process in ERPNext

The Purchase Invoice arrives in ERPNext as a Draft:

1. Go to **Purchase Invoice** list
2. Find invoices with **Is PEPPOL Invoice** checked
3. Review and complete any missing details
4. Submit when ready

## PEPPOL Tracking Fields

Incoming invoices include these fields:

| Field | Description |
|-------|-------------|
| Is PEPPOL Invoice | Checkbox indicating PEPPOL origin |
| PEPPOL Reference | Original invoice reference from sender |
| Sender PEPPOL ID | Sender's PEPPOL Participant ID |
| Received On | When received via PEPPOL |

## Supplier Matching

TAPRNext attempts to match invoices to existing Suppliers:

- **Match found:** Supplier is set automatically
- **No match:** You may need to select or create the Supplier

To improve matching, add PEPPOL IDs to your Suppliers. See [Supplier Setup](06-supplier-setup.md).

## Filtering PEPPOL Invoices

To view only PEPPOL invoices in ERPNext:

1. Go to Purchase Invoice list
2. Add filter: `Is PEPPOL Invoice = Yes`
3. Save as a custom view if needed

## Next Steps

- [Troubleshooting](08-troubleshooting.md) - Common issues and solutions
