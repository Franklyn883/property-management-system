const axios = require('axios');

async function getUserInfo(userId) {
  try {
    const response = await axios.get(`http://user-service:8000/api/v1/accounts/internal/users/${userId}/`, {
      headers: {
        'X-Internal-Api-Key': process.env.USER_SERVICE_INTERNAL_API_KEY,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch user info:", error);
    throw error;
  }
}