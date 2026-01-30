# Company Setup

Configure your company's PEPPOL identity to send and receive e-invoices.

## Find Your PEPPOL ID

Your PEPPOL Participant ID is assigned during TAPRNext registration:

1. Log in to your TAPRNext dashboard
2. Go to **Settings** > **PEPPOL Registration**
3. Copy your **Participant ID** (e.g., `9959:CHE123456789`)

## Configure Company in ERPNext

1. Go to **Company** in ERPNext
2. Scroll to the **PEPPOL** section
3. Enter your **PEPPOL Participant ID**
4. Select the correct **PEPPOL ID Scheme**
5. Save

<!-- Screenshot: Company PEPPOL section -->

## PEPPOL ID Schemes Summary

| Code | Country | Identifier Type |
|------|---------|-----------------|
| `0007:SE:ORGNR` | Sweden | Organization Number |
| `0060:DUNS` | USA / International | D-U-N-S Number |
| `0088:EAN/GLN` | International | EAN/GLN Location Code |
| `0106:NL:KVK` | Netherlands | KvK Number |
| `0151:IN:GSTIN` | India | GST Identification Number |
| `0190:NL:OINO` | Netherlands | OINO (Government) |
| `0199:LEI` | International | Legal Entity Identifier |
| `9914:PEPPOL` | International | Generic PEPPOL ID |
| `9915:AT:VAT` | Austria | VAT Number |
| `9959:CH:UID` | Switzerland | UID Number |

---

## Country-Specific Guidance

### Austria (AT)

**Scheme:** `9915:AT:VAT`

| Field | Details |
|-------|---------|
| Identifier | Austrian VAT Number |
| Format | `ATU` + 8 digits |
| Example | `ATU12345678` |
| Registry | Austrian Tax Authority |

**Notes:**
- The prefix `ATU` is mandatory
- E-invoicing is mandatory for B2G (business-to-government) transactions
- Austria follows the Austrian PEPPOL Authority (BRZ) requirements

---

### Belgium (BE)

**Scheme:** `0208:BE:EN` (Enterprise Number) or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | Enterprise Number or GLN |
| Format (EN) | 10 digits (0 or 1 + 9 digits) |
| Example (EN) | `0123456789` |
| Format (GLN) | 13 digits |
| Example (GLN) | `5400000000001` |

**Notes:**
- Enterprise Number (KBO/BCE) is the primary business identifier
- GLN is also widely accepted
- B2G e-invoicing mandatory via Mercurius platform

---

### Denmark (DK)

**Scheme:** `0184:DK:CVR` (CVR Number) or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | CVR Number or GLN |
| Format (CVR) | 8 digits |
| Example (CVR) | `12345678` |
| Format (GLN) | 13 digits |
| Example (GLN) | `5790000000001` |

**Notes:**
- CVR is the Central Business Register number
- Denmark was one of the first PEPPOL adopters
- NemHandel is the Danish e-invoicing system

---

### Finland (FI)

**Scheme:** `0037:FI:OVT` (OVT Code) or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | OVT Code or GLN |
| Format (OVT) | `0037` + Business ID (8 digits) + optional unit |
| Example (OVT) | `003712345678` |
| Format (GLN) | 13 digits |

**Notes:**
- OVT (Organisaatiotunnus) is derived from the Business ID (Y-tunnus)
- E-invoicing is widely adopted in Finland
- TIEKE manages Finnish PEPPOL coordination

---

### France (FR)

**Scheme:** `0009:FR:SIRET` (SIRET) or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | SIRET Number |
| Format | 14 digits (SIREN + NIC) |
| Example | `12345678901234` |

**Notes:**
- SIRET = SIREN (9 digits) + NIC (5 digits)
- Chorus Pro is the French B2G e-invoicing platform
- B2G e-invoicing mandatory; B2B mandate phased in from 2024-2026

---

### Germany (DE)

**Scheme:** `0204:DE:LWID` (Leitweg-ID) or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | Leitweg-ID (for B2G) or GLN |
| Format (Leitweg) | Variable, includes authority codes |
| Example (Leitweg) | `991-12345-67` |
| Format (GLN) | 13 digits |

**Notes:**
- Leitweg-ID is mandatory for B2G at federal level
- XRechnung is the German invoice standard (PEPPOL BIS compatible)
- ZRE (Zentraler Rechnungseingang) is the central invoice portal

---

### India (IN)

**Scheme:** `0151:IN:GSTIN` (GSTIN)

| Field | Details |
|-------|---------|
| Identifier | GSTIN (GST Identification Number) |
| Format | 15 alphanumeric characters |
| Example | `29ABCDE1234F1Z5` |
| Registry | GST Network (GSTN) |

**GSTIN Format Breakdown:**
- Positions 1-2: State code (01-37)
- Positions 3-12: PAN of the entity
- Position 13: Entity number within state
- Position 14: 'Z' by default
- Position 15: Checksum digit

**Notes:**
- GSTIN is mandatory for GST-registered businesses in India
- India joined PEPPOL in 2021 through OpenPEPPOL
- e-Invoicing via IRP (Invoice Registration Portal) is mandatory for businesses above turnover thresholds
- PEPPOL enables cross-border e-invoicing with Indian entities
- NIC (National Informatics Centre) manages India's e-invoicing infrastructure

**Integration with Indian e-Invoicing:**
- Domestic B2B invoices go through GST e-Invoice system (IRP)
- PEPPOL is primarily used for cross-border transactions
- GSTIN serves as the participant identifier in both systems

---

### Ireland (IE)

**Scheme:** `9914:PEPPOL` or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | Generic PEPPOL or GLN |
| Format (GLN) | 13 digits |

**Notes:**
- Ireland typically uses generic PEPPOL scheme or GLN
- Office of Government Procurement (OGP) manages Irish PEPPOL

---

### Italy (IT)

**Scheme:** `0211:IT:IVA` (VAT) or `0201:IT:CF` (Fiscal Code)

| Field | Details |
|-------|---------|
| Identifier (VAT) | Italian VAT Number |
| Format (VAT) | `IT` + 11 digits |
| Example (VAT) | `IT12345678901` |
| Identifier (CF) | Codice Fiscale |
| Format (CF) | 16 alphanumeric characters |

**Notes:**
- SDI (Sistema di Interscambio) is the primary Italian e-invoicing system
- B2B e-invoicing mandatory since 2019
- PEPPOL is used alongside SDI for cross-border

---

### Luxembourg (LU)

**Scheme:** `0088:EAN/GLN` or `9914:PEPPOL`

| Field | Details |
|-------|---------|
| Identifier | GLN or generic PEPPOL |
| Format (GLN) | 13 digits |

**Notes:**
- Luxembourg typically uses GLN for PEPPOL
- E-invoicing mandatory for B2G transactions

---

### Netherlands (NL)

**Scheme (Private):** `0106:NL:KVK`

| Field | Details |
|-------|---------|
| Identifier | KvK Number (Chamber of Commerce) |
| Format | 8 digits |
| Example | `12345678` |

**Scheme (Government):** `0190:NL:OINO`

| Field | Details |
|-------|---------|
| Identifier | OINO (Government Organization ID) |
| Format | 20 digits |
| Example | `00000001234567890000` |

**Notes:**
- Private companies use KvK number
- Government entities use OINO
- Simplerinvoicing is the Dutch PEPPOL Authority

---

### Norway (NO)

**Scheme:** `0192:NO:ORG` (Organization Number)

| Field | Details |
|-------|---------|
| Identifier | Organization Number |
| Format | 9 digits |
| Example | `123456789` |

**Notes:**
- Norway is a PEPPOL pioneer with high adoption
- E-invoicing mandatory for B2G since 2012
- Difi manages Norwegian PEPPOL

---

### Poland (PL)

**Scheme:** `0088:EAN/GLN` or `9914:PEPPOL`

| Field | Details |
|-------|---------|
| Identifier | GLN or NIP (Tax ID) |
| Format (NIP) | 10 digits |
| Example (NIP) | `1234567890` |

**Notes:**
- KSeF (National e-Invoice System) is Poland's primary system
- PEPPOL used for cross-border transactions
- B2B mandate planned

---

### Portugal (PT)

**Scheme:** `0088:EAN/GLN` or `9914:PEPPOL`

| Field | Details |
|-------|---------|
| Identifier | GLN or NIF (Tax ID) |
| Format (NIF) | 9 digits |
| Example (NIF) | `123456789` |

**Notes:**
- FE-AP (Fatura Eletrónica na Administração Pública) for B2G
- PEPPOL adoption growing for cross-border

---

### Spain (ES)

**Scheme:** `9920:ES:VAT` or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | CIF/NIF (VAT Number) |
| Format | 1 letter + 8 digits or 8 digits + 1 letter |
| Example | `A12345678` or `12345678A` |

**Notes:**
- FACe is the Spanish B2G e-invoicing platform
- Spain uses FacturaE format domestically
- PEPPOL for cross-border transactions

---

### Sweden (SE)

**Scheme:** `0007:SE:ORGNR`

| Field | Details |
|-------|---------|
| Identifier | Organization Number |
| Format | 10 digits |
| Example | `5567891234` |

**Notes:**
- Sweden is a PEPPOL founding member
- High e-invoicing adoption rate
- DIGG manages Swedish PEPPOL

---

### Switzerland (CH)

**Scheme:** `9959:CH:UID`

| Field | Details |
|-------|---------|
| Identifier | UID (Enterprise Identification Number) |
| Format | `CHE` + 9 digits |
| Example | `CHE123456789` |

**Notes:**
- UID is the Swiss Enterprise Identification Number
- Not an EU member but active PEPPOL participant
- TAPRNext is based in Switzerland

---

### United States (US)

**Scheme:** `0060:DUNS` (D-U-N-S Number) or `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier (DUNS) | D-U-N-S Number |
| Format (DUNS) | 9 digits |
| Example (DUNS) | `123456789` |
| Registry | Dun & Bradstreet |

**Alternative Scheme:** `0199:LEI`

| Field | Details |
|-------|---------|
| Identifier | Legal Entity Identifier |
| Format | 20 alphanumeric characters |
| Example | `5493001KJTIIGC8Y1R12` |

**Alternative Scheme:** `9918:US:EIN`

| Field | Details |
|-------|---------|
| Identifier | EIN (Employer Identification Number) |
| Format | 9 digits (XX-XXXXXXX) |
| Example | `12-3456789` |
| Registry | IRS (Internal Revenue Service) |

**Notes:**
- D-U-N-S is widely used for B2B and government contracting
- EIN (also called Federal Tax ID) is the tax identifier
- LEI is recommended for larger organizations and financial sector
- GLN is common for retail and supply chain
- US joined PEPPOL through the Business Payments Coalition
- Federal government increasingly adopting e-invoicing standards
- SAM.gov registration often requires D-U-N-S for government contracts

**Choosing the Right Scheme:**
- **Government contracts:** Use DUNS (required for SAM.gov registration)
- **Financial sector:** Use LEI
- **Retail/Supply chain:** Use GLN
- **General B2B:** Use EIN or DUNS

---

### International / Cross-Border

**Scheme:** `0199:LEI` (Legal Entity Identifier)

| Field | Details |
|-------|---------|
| Identifier | LEI |
| Format | 20 alphanumeric characters |
| Example | `529900T8BM49AURSDO55` |

**Notes:**
- LEI is a global standard for entity identification
- Useful for multinational organizations
- Issued by Local Operating Units (LOUs)

**Scheme:** `0088:EAN/GLN`

| Field | Details |
|-------|---------|
| Identifier | Global Location Number |
| Format | 13 digits |
| Example | `7300010000001` |

**Notes:**
- GS1-issued identifier
- Widely recognized across all PEPPOL countries
- Good fallback when country-specific scheme unavailable

---

## Validation

Ensure your PEPPOL ID in ERPNext matches exactly what's registered in TAPRNext. Mismatches will cause delivery failures.

## Multiple Companies

If you have multiple companies in ERPNext, each can have its own PEPPOL ID. Configure each company separately.

## Next Steps

- [Customer Setup](04-customer-setup.md) - Add PEPPOL IDs to your customers
