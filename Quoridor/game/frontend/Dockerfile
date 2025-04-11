# Step 1: Transfering files in nginx image

FROM nginx:1.27.4
COPY ./configs/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./src /src/
RUN chown root:root /etc/nginx/conf.d/default.conf
RUN chown -R root:root /src
RUN find /src -type f -exec chmod 444 {} \; \
 && find /src -type d -exec chmod 555 {} \;
