FROM node:22-alpine AS build

WORKDIR /app

COPY apps/web/package.json apps/web/pnpm-lock.yaml ./
RUN npm install --global pnpm@10.6.3 && pnpm install --frozen-lockfile

COPY apps/web/ ./

ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN pnpm run build

FROM nginx:1.27-alpine

COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
