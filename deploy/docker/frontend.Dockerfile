FROM node:22-alpine AS build

WORKDIR /frontend

COPY frontend/package*.json /frontend/
RUN npm ci

COPY frontend /frontend

# Production defaults to same-origin API via Nginx reverse proxy.
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM nginx:1.27-alpine

COPY deploy/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
