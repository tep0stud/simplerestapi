FROM python:3.7
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi
RUN pip install -U Flask uWSGI requests mysql-connector-python
WORKDIR /app
COPY app /app
COPY cmd.sh /
# RUN pwd; ls;
EXPOSE 9090 9191
USER uwsgi
CMD ["/cmd.sh"]