const Property = require("../models/property_model");
const { body, validationResult } = require('express-validator');

// Constants for allowed update fields
const ALLOWED_UPDATES = ['title', 'description', 'location', 'price', 'status', 'images'];

// Validation middleware for creating a property
const validateCreateProperty = [
    body('title').notEmpty().withMessage('Title is required'),
    body('location').notEmpty().withMessage('Location is required'),
    body('price').isNumeric().withMessage('Price must be a number'),
];

const createProperty = async (req, res) => {
    try {
        // Check for validation errors
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        const { title, description, location, price } = req.body;

        // Check if user info is available from verifyToken middleware
        console.log("from createProperty: ", JSON.stringify(req.user, null, 2));

        if (!req.user || !req.user.pk) {
            return res.status(401).json({ message: "unauthorized: User info missing" });
        }

        const userId = req.user.pk;
        // Create a New property
        const property = new Property({
            title,
            description,
            location,
            price,
            user: userId, // Attach the user ID from the JWT Token
        });
        await property.save();

        console.log("Property created successfully:", property);
        res.status(201).json({
            message: "Property created successfully",
            property,
        });
    } catch (error) {
        console.error("Error creating property:", error);
        res.status(500).json({ message: "Server Error" });
    }
};

const getAllProperty = async (req, res) => {
    try {
        // get the page and limit from the url
        let { page, limit } = req.query;

        page = parseInt(page) || 1;
        limit = parseInt(limit) || 2;
        const maxLimit = 10; // Set a maximum limit
        limit = Math.min(limit, maxLimit); // Ensure limit does not exceed maxLimit

        const skip = (page - 1) * limit;
        const properties = await Property.find().skip(skip).limit(limit);
        const total = await Property.countDocuments();
        const totalPages = Math.ceil(total / limit);
        const nextPage = page < totalPages ? page + 1 : null;
        const prevPage = page > 1 ? page - 1 : null;

        res.status(200).json({
            page,
            limit,
            total,
            nextPage,
            prevPage,
            totalPages,
            data: properties,
        });
    } catch (error) {
        console.error("Error fetching properties:", error);
        res.status(500).json({ error: error.message });
    }
};

const getPropertyById = async (req, res) => {
    const id = req.params.id;
    try {
        const property = await Property.findById(id);
        if (!property) {
            return res.status(404).json({ message: "Property not found" });
        }
        res.status(200).json(property);
    } catch (error) {
        console.error("Error fetching property by ID:", error);
        res.status(500).json({ error: error.message });
    }
};

const deletePropertyById = async (req, res) => {
    try {
        const id = req.params.id;
        const userId = req.user.pk;

        const property = await Property.findOneAndDelete({ _id: id, user: userId });
        if (!property) {
            return res.status(404).json({ message: "Property not found or unauthorized" });
        }

        console.log("Property deleted successfully:", property);
        return res.status(200).json({ message: "Property deleted successfully" });
    } catch (error) {
        console.error("Delete Error:", error);
        res.status(500).json({ message: "Server error" });
    }
};

// Validation middleware for updating a property
const validateUpdateProperty = [
    body('title').optional().notEmpty().withMessage('Title cannot be empty'),
    body('location').optional().notEmpty().withMessage('Location cannot be empty'),
    body('price').optional().isNumeric().withMessage('Price must be a number'),
];

const updatePropertyById = async (req, res) => {
    try {
        // Check for validation errors
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        const id = req.params.id;
        const userId = req.user.pk;
        const updates = req.body; // The updated fields

        // Validate input: ensure updates only contain allowed fields
        const isValidOperation = Object.keys(updates).every(update => ALLOWED_UPDATES.includes(update));
        if (!isValidOperation) {
            return res.status(400).json({ message: 'Invalid updates!' });
        }

        // Use findOneAndUpdate to optimize database operations
        const updatedProperty = await Property.findOneAndUpdate(
            { _id: id, user: userId },
            updates,
            { new: true, runValidators: true }
        );

        if (!updatedProperty) {
            return res.status(404).json({ message: 'Property not found or unauthorized' });
        }

        console.log("Property updated successfully:", updatedProperty);
        return res.status(200).json({
            message: 'Property Updated successfully',
            updatedProperty,
        });
    } catch (error) {
        console.error('Update Error:', error);
        res.status(500).json({ message: 'Server error' });
    }
};

module.exports = {
    createProperty,
    getAllProperty,
    getPropertyById,
    deletePropertyById,
    updatePropertyById,
    validateCreateProperty,
    validateUpdateProperty,
};
