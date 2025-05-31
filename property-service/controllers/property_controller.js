const Property = require("../models/property_model");

const createProperty = async (req, res) => {
    try {
        const { title, description, location, price } = req.body;

        // Check if user info is available from verifyToken middleware
        console.log("from createProperty: ", JSON.stringify(req.user, null, 2));

        if (!req.user || !req.user.pk) {
            return res
                .status(401)
                .json({ message: "unauthorized: User info missing" });
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

const deletePropertyById = async (req, res) => {
    try {
        const { id } = req.params.id;
        const userId = req.user.pk;

        const property = await Property.findById(id);

        if (!property) {
            return res.status(404).json({ message: "Property not found" });
        }

        //check if the user is the creator of the property
        if (property.user.toString() !== userId) {
            res.status(403).json({
                message: "You are not authorized to delete this property",
            });
        }

        await Property.findByIdAndDelete(id);
        return res
            .status(200)
            .json({ message: "Property deleted successfully" });
    } catch (error) {
        console.error("Delete Error,", error);
        res.status(500).json({ message: "Server error" });
    }
};

const updatePropertyById = async (req, res) => {
    try {
        const { id } = req.params.id;
        const userId = req.user.pk;
        const updates = req.body; // The updated fields

        const property = await Property.findById(id);

        if (!property) {
            return res.status(404).json({ message: "Property not found" });
        }

        //check if the user is the creator of the property
        if (property.user.toString() !== userId) {
            res.status(403).json({
                message: "You are not authorized to delete this property",
            });
        }

        const updatedProperty = await Property.findByIdAndUpdate(id, updates, {
            new: true,
        });
        return res
            .status(200)
            .json({
                message: "Property Updated successfully",
                updatedProperty,
            });
    } catch (error) {
        console.error("Update Error,", error);
        res.status(500).json({ message: "Server error" });
    }
};
module.exports = {
    createProperty,
    getAllProperty,
    getPropertyById,
    deletePropertyById,
    updatePropertyById,
};
