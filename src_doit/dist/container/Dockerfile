FROM python:3.9-slim-bullseye
COPY *.whl .
RUN apt update -qy && \
    apt install -qy pkg-config gcc libcairo2-dev && \
    pip install -qq *.whl && \
    rm *.whl
