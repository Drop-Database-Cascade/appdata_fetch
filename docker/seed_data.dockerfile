FROM python:3.8-alpine

RUN apk add --no-cache bash --repository http://dl-cdn.alpinelinux.org/alpine/v3.15/main ca-certificates curl

COPY /data /initdata_files_appdata_fetch_app/data

COPY /docker/seed_data_entrypoint.sh /
RUN chmod +x /seed_data_entrypoint.sh

ENTRYPOINT ["/seed_data_entrypoint.sh"]