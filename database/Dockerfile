FROM postgres:latest

COPY postgresql.conf /etc/postgresql/postgresql.conf

RUN mkdir -p /var/log/postgresql
RUN chown -R database:database /var/log/postgresql

VOLUME ["/var/lib/postgresql/data", "/var/log/postgresql"]

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
