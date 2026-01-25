FROM node:20-slim
WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ ./

CMD ["npm", "run", "dev"]