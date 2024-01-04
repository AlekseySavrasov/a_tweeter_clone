FROM postgres:latest

ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

COPY postgresql.conf /etc/postgresql/postgresql.conf

RUN mkdir -p /var/log/postgresql
RUN chown -R database:database /var/log/postgresql

VOLUME ["/var/lib/postgresql/data", "/var/log/postgresql"]

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
