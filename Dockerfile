FROM python:3.7

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# required because pip 19+ breaks pyproject.toml editable builds: https://github.com/pypa/pip/issues/6434
ENV PIP_USE_PEP517=false
# Poetry & Pip pinned to latest stable, pip needs to be at least 19+ for installing dashboard as editable
RUN pip3 install --upgrade poetry==0.12.15 virtualenv pip==19.1.1

RUN virtualenv /pyenv
ENV VIRTUAL_ENV /pyenv
ENV PATH=/pyenv/bin:$PATH

COPY dashboard/ /source/dashboard/
COPY pyproject.toml poetry.lock README.md /source/

WORKDIR /source/
# Install app and dependencies in a artifact-able directory
# App is installed by linking source into virtualenv. This is against convention
# but allows the source to be overwritten by a volume during development.
RUN poetry install -v --no-dev --develop dashboard

RUN ln -s /pyenv/bin/dashboard /usr/local/bin/

WORKDIR /
USER root

# configuration for django-uwsgi to work correct in Docker environment
ENV UWSGI_GID root
ENV UWSGI_UID root
ENV UWSGI_MODULE dashboard.wsgi
# serve static files (to caching proxy) from collected/generated static files
ENV UWSGI_STATIC_MAP /static=/srv/dashboard/static
# set proxy and browser caching for static files to 1 month
ENV UWSGI_STATIC_EXPIRES /* 2678400
ENV TOOLS_DIR /usr/local/bin/
ENV VENDOR_DIR /source/vendor/

# collect all static files form all django applications into static files directory
RUN /usr/local/bin/dashboard collectstatic

# Compress JS/CSS before serving, using django-compressor, run after collectstatic
# COMPRESS=1 is a hack to disable django_uwsgi app as it currently conflicts with compressor
# https://github.com/django-compressor/django-compressor/issues/881
RUN env COMPRESS=1 /usr/local/bin/dashboard compress

EXPOSE 8000

ENTRYPOINT [ "/usr/local/bin/dashboard" ]

CMD [ "dashboard_prdserver" ]
