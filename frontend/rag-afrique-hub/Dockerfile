FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

# VITE_API_URL est bakée au build — elle doit correspondre à l'URL
# que le navigateur utilisera pour atteindre le backend.
ARG VITE_API_URL=http://localhost:8000
ARG VITE_API_KEY=

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_KEY=$VITE_API_KEY

COPY . .
RUN npm run build

# Nginx pour servir le build statique
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
