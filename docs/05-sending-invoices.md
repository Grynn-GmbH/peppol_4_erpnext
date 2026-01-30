# Sending Sales Invoices

Send e-invoices to your customers via the PEPPOL network.

## Prerequisites

Before sending, ensure:
- [x] PEPPOL is enabled in PEPPOL Settings
- [x] Your Company has a PEPPOL ID configured
- [x] The Customer has a PEPPOL ID configured
- [x] TAPRNext is connected to your ERPNext

## Step 1: Create and Submit Invoice

1. Create a **Sales Invoice** in ERPNext
2. Select a customer with a PEPPOL ID
3. Add line items as usual
4. **Submit** the invoice

> **Note:** Only submitted invoices can be sent via PEPPOL.

## Step 2: Mark for PEPPOL

After submitting:

1. Click the **Mark for PEPPOL** button
2. The `send_via_peppol` checkbox is set to true
3. The `peppol_status` changes to **Ready**

<!-- Screenshot: Mark for PEPPOL button -->

Alternatively, you can manually:
1. Check the **Send via PEPPOL** checkbox in the PEPPOL section
2. Save

## Step 3: TAPRNext Picks Up the Invoice

TAPRNext runs batch jobs that:

1. Fetch invoices where `send_via_peppol = 1` and `peppol_status = Ready`
2. Convert to PEPPOL UBL format
3. Deliver via the PEPPOL network
4. Update the status in your ERPNext

This happens automatically - no action required.

## Understanding Status

| Status | Meaning |
|--------|---------|
| *(empty)* | Not marked for PEPPOL |
| **Ready** | Waiting for TAPRNext to pick up |
| **Sent** | Picked up and sent to PEPPOL network |
| **Delivered** | Confirmed delivered to recipient |
| **Failed** | Delivery failed (check error message) |

## Tracking Fields

After delivery, these fields are populated:

| Field | Description |
|-------|-------------|
| TAPRNext Document | Reference ID in TAPRNext |
| Sent On | Timestamp when sent |
| MLR Status | AS4 network delivery status |
| MLR Description | Detailed delivery response |
| Error Message | Error details (if failed) |

## Viewing Delivery Status in TAPRNext

For detailed tracking:

1. Log in to TAPRNext dashboard
2. Go to **Outbound Documents**
3. Find your invoice by reference
4. View full delivery history and MLR response

## What If Delivery Fails?

If status shows **Failed**:

1. Check the **Error Message** field
2. Common issues:
   - Invalid recipient PEPPOL ID
   - Recipient not found on network
   - Document validation errors
3. Fix the issue and re-mark for PEPPOL

## Next Steps

- [Supplier Setup](06-supplier-setup.md) - Prepare to receive invoices
- [Troubleshooting](08-troubleshooting.md) - Common issues and solutions
