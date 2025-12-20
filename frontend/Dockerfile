FROM node:20-slim
WORKDIR /app

# Копируем из подпапки frontend/
COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ ./

CMD ["npm", "run", "dev"]