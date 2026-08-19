# CASL Consent Record Schema — Mandatory

Every commercial message must have a corresponding consent record before send.
This schema maps to the Airtable `consent_log` table.

```json
{
  "consent_id": "UUID",
  "contact_id": "string",
  "contact_email": "string",
  "contact_phone": "string (E.164) | null",
  "consent_type": "express | implied",
  "channel": "email | sms",
  "consent_source": "string (e.g. 'form_submission_2024-01-15', 'public_business_listing')",
  "consent_date": "ISO 8601",
  "consent_expiry": "ISO 8601 | null",
  "unsubscribed": false,
  "unsubscribe_date": "ISO 8601 | null",
  "unsubscribe_method": "reply | link | null",
  "messages_sent": 0,
  "last_message_date": "ISO 8601 | null",
  "suppression_list": false,
  "notes": "string | null"
}
```

## Rules
- implied consent email: expires 2 years from consent_date
- implied consent: max 2 messages total (Script 1 + Script 2 only)
- express consent SMS: required before any SMS send
- unsubscribed: true → suppression_list: true, no further sends ever
- consent_id referenced in every executor log entry — never the email address
