const jwt = require("jsonwebtoken");

const authentication = (req, res, next) => {
    const token = req.headers["authorization"]?.split(" ")[1];
    if (!token) res.status(401).json({ error: "Access denied" });
    try {
        const decoded = jwt.verify(token, process.JWT_SECRET);
        req.user = decoded; // Attach user info
        next();
    } catch (error) {
        res.status(403).json({ error: "invalid token" });
    }
};
