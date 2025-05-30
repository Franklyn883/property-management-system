const jwt = require("jsonwebtoken");

// Use the same secret your django services uses

const JWT_SECRET = process.env.JWT_SECRET;

const verifyToken = (req, res, next) => {
    const authHeader = req.headers.authorization;

    if (!authHeader || authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ Message: "No token provided" });
    }

    const token = authHeader.split(" ")[1];

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = decoded; //decoded contains userId, email and other details
        next();
    } catch (error) {
        return res.status(401).json({ message: "Token is invalid or expired" });
    }
};


module.exports = verifyToken