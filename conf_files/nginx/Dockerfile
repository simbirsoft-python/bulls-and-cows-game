FROM nginx:1.17.1-alpine

ARG ADMIN_USER
ARG ADMIN_PASSWORD

RUN apk add apache2-utils && \
    htpasswd -cbB /etc/nginx/.htpasswd ${ADMIN_USER} ${ADMIN_PASSWORD}