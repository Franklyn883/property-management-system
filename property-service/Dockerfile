FROM node:18-slim

WORKDIR /usr/src/app


COPY package.json .  
RUN npm install

# ✅ Copy the rest of your app files (including server.js)
COPY . .

# ✅ Optional: expose a port if your app runs on one (e.g., 3000)
EXPOSE 5002

# ✅ Use npm start as the default command
CMD ["npm", "start"]
