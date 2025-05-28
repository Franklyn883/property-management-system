const mongoose = require("mongoose");

const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URL);
        console.log("MongoDB connected for Property Service");
    } catch (error) {
        console.error("DB connection error:", error);
        process.exit(1);
    }
};

module.exports = connectDB;
