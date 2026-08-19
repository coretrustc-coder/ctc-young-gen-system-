export const authMiddleware = (req, res, next) => {
  const authHeader = req.headers["authorization"];
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  if (authHeader.split(" ")[1] !== process.env.HERMES_API_KEY) {
    return res.status(403).json({ error: "Forbidden" });
  }
  next();
};
