FROM python:3.9
LABEL maintainer="akm-xdd"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python3 -m venv /py && \
    /py/bin/pip3 install --upgrade pip && \
    /py/bin/pip3 install -r /tmp/requirements.txt && \
    if [$DEV = "true"]; \
        then /py/bin/pip3 install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
        adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"

USER django-user