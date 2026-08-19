# CoreTrust Hermes System — Claude Code Context

## What This Project Is
Multi-agent AI pipeline for CoreTrust Consulting.
Handles 4 service lines: Credit Intake, Inbound Leads, Cold GTA Outreach, AI Agent Sales.
Stack: Node.js · Express · Anthropic API · n8n · Airtable · Gmail · Twilio

## Who You Are Working With
Trevon — founder of CoreTrust Consulting, Brampton ON.
Legal Studies background (University of Waterloo). Compliance-first operator.
Direct communication style. No filler. Give the answer.

## CoreTrust Business Domains (This System)
1. Credit dispute consulting — Canadian consumer rights, dispute strategy, score-building
2. Business funding strategy — credit leverage, account staging, funding readiness
3. AI agent development + integration — custom pipelines, websites, SEO, chatbots, CRM
4. Canadian law paralegal consulting — consumer law education, document prep, compliance review

## Hard Rules for This Codebase (Never Break These)
- No guaranteed outcome language in any client-facing output
- No PII in log payloads — use contact_id references only
- Compliance agent runs SECOND, before Analyst — never rearrange pipeline order
- Unsubscribe mechanism must be present before any email send executes
- Express SMS consent required — implied consent covers email only
- CASL footer appended to every commercial email
- Disclaimer appended to every client-facing output (see core/disclaimers.md)
- Service agreement must be signed before any paid engagement starts

## Files You Need to Know
- core/strategist_context.md — full CoreTrust business context for agents
- core/execution_rules.md — compliance enforcement logic
- core/disclaimers.md — mandatory disclaimer library
- agents/*.md — individual agent system prompts
- api/server.js — Anthropic API bridge (the engine)

## When Writing or Modifying Code
- All agent calls go through api/server.js → callClaude()
- Model: claude-sonnet-4-5 (do not change without approval)
- Never hardcode the API key — it lives in .env as ANTHROPIC_API_KEY
- Always validate stage against the allowed list before calling the API
- Rate limiter is active — 60 req/min per IP
- Server binds to 127.0.0.1 only — never 0.0.0.0

## Project Status
- Architecture: Complete
- Airtable schema: Must be built before n8n wiring
- Legal docs: Must be finalized before client onboarding
- Build order: See README.md Part 9
