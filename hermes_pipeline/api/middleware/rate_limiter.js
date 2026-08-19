const requests = new Map();
const WINDOW_MS = 60 * 1000;
const MAX_REQUESTS = 60;

export const rateLimiter = (req, res, next) => {
  const ip = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  const timestamps = (requests.get(ip) || []).filter(t => t > now - WINDOW_MS);
  if (timestamps.length >= MAX_REQUESTS) {
    return res.status(429).json({ error: "Rate limit exceeded." });
  }
  timestamps.push(now);
  requests.set(ip, timestamps);
  next();
};
