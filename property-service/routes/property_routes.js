const {
    createProperty,
    getAllProperty,
    getPropertyById,
} = require("../controllers/property_controller");
const verifyToken = require("../middleware/auth_middleware");
const express = require("express");

// instantiate the express router
const router = express.Router();

router.post("/", createProperty);
router.get("/", verifyToken, getAllProperty);
router.get("/:id", getPropertyById);

module.exports = router;
