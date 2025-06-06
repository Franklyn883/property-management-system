const express = require('express');
const router = express.Router();
const {
    createProperty,
    getAllProperty,
    getPropertyById,
    deletePropertyById,
    updatePropertyById,
    validateCreateProperty,
    validateUpdateProperty,
} = require('../controllers/property_controller');
const verifyToken = require('../middleware/auth_middleware');

// Route to create a property with validation
router.post('/', verifyToken, validateCreateProperty, createProperty);

// Route to get all properties
router.get('/', getAllProperty);

// Route to get a property by ID
router.get('/:id', getPropertyById);

// Route to delete a property by ID
router.delete('/:id', verifyToken, deletePropertyById);

// Route to update a property by ID with validation
router.put('/:id', verifyToken, validateUpdateProperty, updatePropertyById);

module.exports = router;
