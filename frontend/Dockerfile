FROM node:18-alpine AS build

WORKDIR /src
COPY shared/ ./shared/
COPY voice/ ./voice/
COPY frontend/package.json frontend/package-lock.json ./frontend/
WORKDIR /src/frontend
RUN npm install --prefer-offline --no-audit
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /src/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
