FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

# VITE_API_URL est bakée au build — elle doit correspondre à l'URL
# que le navigateur utilisera pour atteindre le backend.
# IMPORTANT : Ne JAMAIS passer de secrets (API_KEY, etc.) comme ARG/ENV
# Vite : toute variable VITE_* se retrouve en clair dans le bundle JS public.
ARG VITE_API_URL=http://localhost:8000

ENV VITE_API_URL=$VITE_API_URL

COPY . .
RUN npm run build

# Nginx pour servir le build statique
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
