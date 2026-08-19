// CoreTrust Hermes API Bridge — v3
// Engine: Anthropic API (Claude claude-sonnet-4-5)
// Bridges: n8n → Claude agent system prompts
// Auth-gated. Rate-limited. No shell injection. 127.0.0.1 only.

import express from "express";
import Anthropic from "@anthropic-ai/sdk";
import { readFileSync } from "fs";
import { randomUUID } from "crypto";
import { authMiddleware } from "./middleware/auth.js";
import { validateAgentRequest } from "./middleware/validator.js";
import { rateLimiter } from "./middleware/rate_limiter.js";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(rateLimiter);
app.use("/run-agent", authMiddleware);

// Anthropic client — reads ANTHROPIC_API_KEY from .env automatically
const anthropic = new Anthropic();
const MODEL = "claude-sonnet-4-5";

// Load strategist context once at startup (injected into every agent call)
const STRATEGIST_CONTEXT = readFileSync("./core/strategist_context.md", "utf8");

async function callClaude(agentSystemPrompt, userContent) {
  const systemPrompt =
    `${STRATEGIST_CONTEXT}\n\n---\n\n${agentSystemPrompt}\n\n` +
    `CRITICAL: Respond ONLY with a valid JSON object. No markdown fences. No preamble. ` +
    `No explanation. Raw JSON only.`;

  const message = await anthropic.messages.create({
    model: MODEL,
    max_tokens: 2048,
    system: systemPrompt,
    messages: [
      {
        role: "user",
        content:
          typeof userContent === "string"
            ? userContent
            : JSON.stringify(userContent, null, 2),
      },
    ],
  });

  const raw = message.content[0]?.text;
  if (!raw) throw new Error("Empty response from Claude");

  // Strip any markdown fences in case model adds them despite instructions
  const cleaned = raw
    .replace(/^```(?:json)?\s*/m, "")
    .replace(/\s*```$/m, "")
    .trim();

  return JSON.parse(cleaned);
}

app.post("/run-agent", validateAgentRequest, async (req, res) => {
  const { input, stage, session_id } = req.body;

  let agentPrompt;
  try {
    agentPrompt = readFileSync(`./agents/${stage}.md`, "utf8");
  } catch (e) {
    return res
      .status(400)
      .json({ error: `No agent definition found for stage: ${stage}` });
  }

  const requestId = randomUUID();
  console.log(`[${requestId}] Stage: ${stage} | Session: ${session_id}`);

  try {
    const output = await callClaude(agentPrompt, input);
    console.log(`[${requestId}] Success`);
    return res.status(200).json({ stage, session_id, output, request_id: requestId });
  } catch (e) {
    console.error(`[${requestId}] Failed: ${e.message}`);
    return res.status(500).json({
      error: "Agent call failed",
      stage,
      detail: e.message,
      request_id: requestId,
    });
  }
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", model: MODEL, timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, "127.0.0.1", () => {
  console.log(`CoreTrust Hermes API → http://127.0.0.1:${PORT}`);
  console.log(`Model: ${MODEL}`);
});
