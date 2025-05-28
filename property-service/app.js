const express = require("express");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const propertyRoutes = require("./routes/property_routes");

dotenv.config();

const connectDB = require("./config/db");

const app = express();

app.use(express.json());

// Connect to DB
connectDB();

// app.use("/api/v1/properties", propertyRoutes);
app.get("/", (req, res) => {
    res.send("Property service is live");
});

module.exports = app;
