const mongoose = require("mongoose");

const propertySchema = new mongoose.Schema(
    {
        title: { type: String, required: true },
        description: String,
        location: String,
        price: Number,
        images: [String],
        status: {
            type: String,
            enum: ["available", "booked", "rented"],
            default: "available",
        },
        userId: { type: String, required: true },
    },
    { timestamps: true }
);

const Property = mongoose.model("Property", propertySchema);
module.exports = Property;
