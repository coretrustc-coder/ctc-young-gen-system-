const VALID_STAGES = ["planner", "compliance", "analyst", "executor", "critic"];

export const validateAgentRequest = (req, res, next) => {
  const { input, stage, session_id } = req.body;
  if (!input || typeof input !== "object") {
    return res.status(400).json({ error: "input must be a JSON object" });
  }
  if (!VALID_STAGES.includes(stage)) {
    return res.status(400).json({ error: `stage must be one of: ${VALID_STAGES.join(", ")}` });
  }
  if (!session_id || typeof session_id !== "string") {
    return res.status(400).json({ error: "session_id is required" });
  }
  next();
};
