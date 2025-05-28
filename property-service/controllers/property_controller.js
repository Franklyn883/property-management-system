const Property = require("../models/property_model");

const createProperty = async (req, res) => {
    // const { title, description, price, location, images } = req.body;
    const userId = req.user.id; // from auth middleware
    try {
        const property = new Property({ ...req.body, userId: userId });
        const saved = await property.save();
        res.status(201).json(property);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
};

const getAllProperty = async (req, res) => {
    try {
        const properties = await Property.find();
        res.status(200).json(properties);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getPropertyById = async (req, res) => {
    const id = req.params.id;
    try {
        const property = await Property.findById(id);
        res.status(200).json(property);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
};

module.exports = { createProperty, getAllProperty, getPropertyById };
