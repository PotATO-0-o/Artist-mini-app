FROM nginx:1.23-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
COPY . /usr/share/nginx/html
RUN chmod -R 755 /usr/share/nginx/html