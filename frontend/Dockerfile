# Node.js Lightweight Alpine Base Image
FROM node:20-alpine

# Set execution directory inside the container
WORKDIR /app

# Copy package definition files to leverage Docker build layer caching
COPY package*.json ./

# Install project dependencies cleanly
RUN npm install

# Copy application source files
COPY . .

# Expose Vite dev server port
EXPOSE 3000

# Command to launch Vite dev server inside container
CMD ["npm", "run", "dev"]