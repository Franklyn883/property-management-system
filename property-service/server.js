const app = require("./app");
const dotenv = require("dotenv");
dotenv.config();

const PORT = process.env.PORT || 5002;

app.listen(PORT, () => {
    console.log(`Property service running on port ${PORT}`);
});
