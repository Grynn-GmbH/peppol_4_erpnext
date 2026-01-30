# Troubleshooting & FAQ

Common issues and solutions for PEPPOL integration.

## Sending Issues

### Invoice Stuck on "Ready" Status

**Symptom:** Invoice marked for PEPPOL but status never changes from "Ready"

**Solutions:**
1. Verify TAPRNext is connected to your ERPNext
2. Check TAPRNext dashboard for connection errors
3. Ensure your ERPNext URL is accessible from TAPRNext
4. Verify API credentials are valid

### Invoice Shows "Failed" Status

**Symptom:** PEPPOL status is "Failed" with an error message

**Common causes:**
- **Invalid recipient PEPPOL ID:** Verify the customer's PEPPOL ID is correct
- **Recipient not on network:** Customer may not be registered
- **Validation error:** Invoice may be missing required fields

**Solutions:**
1. Check the Error Message field for details
2. Verify Customer PEPPOL ID in directory.peppol.eu
3. Correct the issue and re-mark for PEPPOL

### "Mark for PEPPOL" Button Missing

**Symptom:** Button doesn't appear on submitted Sales Invoice

**Solutions:**
1. Ensure PEPPOL is enabled in PEPPOL Settings
2. Check that the Customer has a PEPPOL ID
3. Verify your Company has a PEPPOL ID
4. Clear browser cache and reload

## Receiving Issues

### Invoices Not Appearing in ERPNext

**Symptom:** Invoices visible in TAPRNext but not in ERPNext

**Solutions:**
1. Ensure invoices are approved in TAPRNext
2. Check TAPRNext connection to ERPNext
3. Verify API credentials have sufficient permissions
4. Check ERPNext error logs for API errors

### Supplier Not Matched

**Symptom:** Purchase Invoice created but Supplier is empty

**Solutions:**
1. Add the sender's PEPPOL ID to the Supplier record
2. See [Supplier Setup](06-supplier-setup.md) for details

## Connection Issues

### TAPRNext Cannot Connect to ERPNext

**Symptoms:**
- Connection test fails
- Invoices not picked up or delivered

**Solutions:**
1. Verify your ERPNext URL is correct and accessible
2. Check API Key and Secret are valid
3. Ensure the API user has required roles:
   - Sales User (for Sales Invoices)
   - Purchase User (for Purchase Invoices)
4. Check firewall/security rules allow TAPRNext IPs

### API Authentication Errors

**Symptom:** 401 or 403 errors in logs

**Solutions:**
1. Regenerate API credentials in ERPNext
2. Update credentials in TAPRNext
3. Verify user account is not disabled

## Status Reference

### Sales Invoice PEPPOL Status

| Status | Meaning | Action |
|--------|---------|--------|
| *(empty)* | Not for PEPPOL | No action needed |
| Ready | Waiting for pickup | Wait for TAPRNext batch |
| Sent | In transit | Wait for delivery confirmation |
| Delivered | Successfully delivered | Complete |
| Failed | Delivery failed | Check error, fix, retry |

### MLR (Message Level Response)

The MLR fields show AS4 network delivery status:

| MLR Status | Meaning |
|------------|---------|
| Accepted | Message delivered successfully |
| Rejected | Recipient rejected the message |
| Error | Network or technical error |

## FAQ

### Q: How long does delivery take?

Typically within minutes. If status stays "Ready" for more than an hour, check the connection.

### Q: Can I resend a failed invoice?

Yes. Fix the issue and click "Mark for PEPPOL" again. This resets the status to "Ready".

### Q: What invoice formats does PEPPOL use?

PEPPOL uses UBL (Universal Business Language) XML format. TAPRNext handles the conversion automatically.

### Q: Do I need to pay per invoice?

Pricing depends on your TAPRNext subscription. Contact TAPRNext for details.

### Q: Can I send to non-PEPPOL customers?

No. Both sender and recipient must be registered on the PEPPOL network.

### Q: Which countries support PEPPOL?

PEPPOL is used across Europe and expanding globally. Check [peppol.org](https://peppol.org) for current coverage.

## Getting Help

- **TAPRNext Support:** Contact via your TAPRNext dashboard
- **PEPPOL Directory:** [directory.peppol.eu](https://directory.peppol.eu/)
- **PEPPOL Information:** [peppol.org](https://peppol.org)

## Documentation Index

- [Quick Start](00-quick-start.md)
- [Overview & Prerequisites](01-overview-prerequisites.md)
- [Installation](02-installation.md)
- [Company Setup](03-company-setup.md)
- [Customer Setup](04-customer-setup.md)
- [Sending Invoices](05-sending-invoices.md)
- [Supplier Setup](06-supplier-setup.md)
- [Receiving Invoices](07-receiving-invoices.md)
