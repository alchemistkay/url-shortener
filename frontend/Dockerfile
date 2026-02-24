# ============================================
# Use Nginx to serve static files
# ============================================

FROM nginx:alpine

# Copy static files to Nginx html directory
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Nginx runs automatically (default CMD)