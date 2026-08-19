# Execution Rules — Hard Limits

## Agent Execution Order (FIXED — do not rearrange)
1. Planner
2. Compliance Gate    ← BLOCKING. Halts on non-compliant input.
3. Analyst
4. Executor
5. Critic             ← BLOCKING. Enforces disclaimer + tone. Max 3 retries then dead-letter.
6. Memory Write

## Kill Conditions
- Compliance Gate: compliant: false
- Critic: 3 consecutive rejections
- consent_check: valid: false before any send action
- Any tool: 5xx error twice in a row
- Input contains raw PII without pii_authorized: true in session

## Retry Policy
- Tool failure: retry once after 2s. Second failure = dead-letter + alert.
- Agent output malformed: re-call once with error context. Second failure = dead-letter.

## Idempotency Rule
Every Executor action key: {session_id}_{task_id}_{action_name}
Key exists in session log → skip. Do not re-execute.

## CASL Rules
- Implied consent (publicly listed business contact): email only, max 2 messages, expires 2 years
- Express consent required: SMS, follow-ups beyond sequence, re-engagement after expiry
- Every send logs: contact_id, channel, consent_type, consent_source, timestamp
- Unsubscribe processed same day via automation
- Suppression list checked before every send

## Ontario CPA 2002
- 10-day cooling-off period disclosed in service agreement for internet agreements
- Total pricing clear and inclusive before agreement signed
- No misleading performance representations in outreach

## Data Rules
- No raw PII in tool call payloads — contact_id references only
- Session data: deleted 30 days after session close unless retention authorized in service agreement
- Audit logs: retained minimum 2 years
- Breach protocol: notify OPC within 72 hours of discovering breach with real risk of significant harm (PIPEDA s.10.1)

## Compliance Jurisdiction Priority
1. Canadian law (PIPEDA, CASL, CPA 2002, Criminal Code)
2. US consumer law (FCRA, FDCPA, FTC Act)
Conflict → most restrictive wins.
