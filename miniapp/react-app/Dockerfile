FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY public ./public
COPY src ./src

# Default: nginx will proxy /api to backend
ARG REACT_APP_API_URL=/api
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Optional build-time envs (CRA reads REACT_APP_*)
ARG REACT_APP_BOT_USERNAME=
ENV REACT_APP_BOT_USERNAME=$REACT_APP_BOT_USERNAME

ARG REACT_APP_MANAGER_TELEGRAM=
ENV REACT_APP_MANAGER_TELEGRAM=$REACT_APP_MANAGER_TELEGRAM

RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

