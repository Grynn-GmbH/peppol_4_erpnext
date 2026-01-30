# Installation Guide

## Step 1: Sign Up for TAPRNext

1. Go to [cloud.tapr.ch/dashboard/signup?product=inflow](https://cloud.tapr.ch/dashboard/signup?product=inflow)
2. Create your account
3. Complete the PEPPOL registration process
4. Note your assigned **PEPPOL Participant ID**

## Step 2: Install the App in ERPNext

```bash
# Get the app
bench get-app https://github.com/[repo]/peppol_4_erpnext

# Install on your site
bench --site your-site.com install-app peppol_4_erpnext

# Run migrations
bench --site your-site.com migrate
```

## Step 3: Enable PEPPOL in ERPNext

1. Go to **PEPPOL Settings** in ERPNext
2. Check **Enable PEPPOL**
3. Save

<!-- Screenshot: PEPPOL Settings page -->

## Step 4: Generate API Credentials in ERPNext

TAPRNext needs API access to your ERPNext instance.

1. Create a dedicated user for TAPRNext (e.g., `taprnext@yourcompany.com`)
2. Assign appropriate roles (Sales User, Purchase User)
3. Generate API keys:
   - Go to the user's profile
   - Click **API Access** > **Generate Keys**
   - Copy the **API Key** and **API Secret**

> **Security Note:** Store these credentials securely. The API Secret is shown only once.

## Step 5: Connect TAPRNext to ERPNext

In your TAPRNext dashboard:

1. Go to **Settings** > **ERPNext Connection**
2. Enter your ERPNext URL (e.g., `https://erp.yourcompany.com`)
3. Enter the API Key and API Secret
4. Click **Test Connection**
5. Save once the test succeeds

## Verification

To verify the installation:

1. In ERPNext, go to any **Company** record
2. You should see a new **PEPPOL** section
3. Go to any **Sales Invoice**
4. You should see PEPPOL fields and a **Mark for PEPPOL** button

## Next Steps

- [Company Setup](03-company-setup.md) - Configure your PEPPOL identity
