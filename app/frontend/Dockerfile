FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
RUN apk add --no-cache nginx gettext curl && \
    mkdir -p /usr/share/nginx/html /run/nginx && \
    rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV API_HOST=triage-backend
ENV API_SCHEME=http
EXPOSE 80
ENTRYPOINT ["/docker-entrypoint.sh"]
