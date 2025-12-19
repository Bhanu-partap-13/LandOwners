FROM node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Use --legacy-peer-deps to bypass React 19 vs React 18 conflict
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]