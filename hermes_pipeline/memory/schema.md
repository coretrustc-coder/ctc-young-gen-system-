# Session Context Object — Full Schema

```json
{
  "session_id": "UUID",
  "created_at": "ISO 8601",
  "workflow": "lead_conversion | credit_intake | outreach | ai_agent_sales | custom",
  "contact_id": "string",
  "workflow_stage": "string",
  "prior_interactions": 0,
  "pii_authorized": false,
  "consent": {
    "email": {
      "valid": true | false,
      "consent_type": "express | implied",
      "consent_source": "string",
      "consent_date": "ISO 8601",
      "expires": "ISO 8601 | null",
      "unsubscribed": false
    },
    "sms": {
      "valid": true | false,
      "consent_type": "express",
      "consent_source": "string",
      "consent_date": "ISO 8601",
      "expires": "ISO 8601 | null",
      "unsubscribed": false
    }
  },
  "idempotency_log": {
    "{session_id}_{task_id}_{action_name}": "ISO 8601"
  },
  "agent_outputs": {
    "planner": {},
    "compliance": {},
    "analyst": {},
    "executor": {},
    "critic": {}
  },
  "dead_letter": false,
  "dead_letter_reason": "string | null",
  "audit_trail": [
    {
      "timestamp": "ISO 8601",
      "agent": "string",
      "action": "string",
      "result": "string"
    }
  ]
}
```
