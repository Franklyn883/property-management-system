const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../app'); // Import your Express app
const Property = require('../models/property_model');

// Mock the verifyToken middleware
jest.mock('../middleware/auth_middleware', () => (req, res, next) => {
    req.user = { pk: '123456789' }; // Mock user ID
    next();
});

describe('Property Controller Tests', () => {
    beforeAll(async () => {
        // Connect to a test database
        await mongoose.connect(process.env.MONGO_URL_TEST, { useNewUrlParser: true, useUnifiedTopology: true });
    });

    afterAll(async () => {
        // Disconnect from the test database
        await mongoose.connection.close();
    });

    beforeEach(async () => {
        // Clear the Property collection before each test
        await Property.deleteMany({});
    });

    test('should create a new property', async () => {
        const propertyData = {
            title: 'Test Property',
            description: 'This is a test property',
            location: 'Test Location',
            price: 100000,
        };

        const response = await request(app)
            .post('/api/v1/properties')
            .send(propertyData);

        expect(response.status).toBe(201);
        expect(response.body.message).toBe('Property created successfully');
        expect(response.body.property.title).toBe(propertyData.title);
    });

    test('should get all properties', async () => {
        // Create a test property
        await Property.create({
            title: 'Test Property',
            description: 'This is a test property',
            location: 'Test Location',
            price: 100000,
            user: '123456789',
        });

        const response = await request(app).get('/api/v1/properties');

        expect(response.status).toBe(200);
        expect(response.body.data.length).toBe(1);
    });

    test('should get a property by ID', async () => {
        // Create a test property
        const property = await Property.create({
            title: 'Test Property',
            description: 'This is a test property',
            location: 'Test Location',
            price: 100000,
            user: '123456789',
        });

        const response = await request(app).get(`/api/v1/properties/${property._id}`);

        expect(response.status).toBe(200);
        expect(response.body.title).toBe(property.title);
    });

    test('should delete a property by ID', async () => {
        // Create a test property
        const property = await Property.create({
            title: 'Test Property',
            description: 'This is a test property',
            location: 'Test Location',
            price: 100000,
            user: '123456789',
        });

        const response = await request(app).delete(`/api/v1/properties/${property._id}`);

        expect(response.status).toBe(200);
        expect(response.body.message).toBe('Property deleted successfully');
    });

    test('should update a property by ID', async () => {
        // Create a test property
        const property = await Property.create({
            title: 'Test Property',
            description: 'This is a test property',
            location: 'Test Location',
            price: 100000,
            user: '123456789',
        });

        const updates = {
            title: 'Updated Property',
            price: 150000,
        };

        const response = await request(app)
            .put(`/api/v1/properties/${property._id}`)
            .send(updates);

        expect(response.status).toBe(200);
        expect(response.body.message).toBe('Property Updated successfully');
        expect(response.body.updatedProperty.title).toBe(updates.title);
    });
}); 