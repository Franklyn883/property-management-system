const jwt = require("jsonwebtoken");
const axios = require("axios");
// Use the same secret your django services uses

const JWT_SECRET = process.env.JWT_SECRET;

const verifyToken = async (req, res, next) => {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ Message: "No token provided" });
    }

    const token = authHeader.split(" ")[1];
    console.log("Sending token to user-service:", token);

    try {
        // Forward token to Django user-service for validation
        const response = await axios.get(
            "http://user-service:8000/api/v1/accounts/user",
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        );
        req.user = response.data; // attach user data to request
        console.log(req.user)
        next();
    } catch (error) {
        console.error("verifyToken error:", error.message);
        return res.status(401).json({ message: "Token is invalid or expired" });
    }
};

module.exports = verifyToken;
