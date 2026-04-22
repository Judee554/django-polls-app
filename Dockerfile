FROM nginx:stable-alpine

RUN rm -rf /usr/share/nginx/html/*
COPY index.html /usr/share/nginx/html/
COPY sgustyle.css /usr/share/nginx/html/
COPY sguscript.js /usr/share/nginx/html/

# Optional images/assets
COPY grenada.jpeg /usr/share/nginx/html/
COPY grenada-updated.jpeg /usr/share/nginx/html/

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
