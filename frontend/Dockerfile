FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 5173

# Run
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
