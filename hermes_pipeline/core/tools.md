# Available Tools — Agent Access Matrix

| Tool | Description | Agents Allowed |
|------|-------------|----------------|
| gmail_send | Send email via Gmail | Executor |
| gmail_read | Read/parse inbox | Planner, Analyst |
| twilio_sms | Send SMS (express consent required) | Executor |
| airtable_read | Pull lead/client/consent records | Planner, Analyst |
| airtable_write | Write/update records | Executor |
| webhook_trigger | Trigger external n8n webhook | Executor |
| doc_parse | Parse uploaded documents | Analyst |
| memory_read | Read session context | All |
| memory_write | Write to session context | Executor, Critic |
| consent_check | Verify CASL consent record exists | Compliance, Executor |
| disclaimer_append | Append correct disclaimer to output | Critic |

## Critical Tool Rules
- Executor is the ONLY agent that calls side-effect tools (send, write, trigger)
- consent_check must return valid: true before gmail_send or twilio_sms runs
- twilio_sms requires express consent — implied consent is NOT sufficient for SMS
- disclaimer_append called by Critic on every client-facing output — not optional
- All tool calls logged: timestamp + input_reference + result

## Tool Schemas

### consent_check
{
  "contact_id": "string",
  "channel": "email | sms",
  "consent_type_required": "express | implied"
}
Returns: { "valid": true | false, "consent_type": "string", "expires": "ISO 8601 | null" }

### gmail_send
{
  "to": "string",
  "subject": "string",
  "body": "string",
  "disclaimer_type": "1 | 2 | 3 | 4 | 5",
  "casl_footer": true,
  "thread_id": "string | null"
}

### twilio_sms
{
  "to": "string (E.164)",
  "body": "string (max 160 chars)",
  "consent_verified": true
}
Note: consent_verified must be explicitly set to true. Executor calls consent_check first.
