FROM python:3.10-slim-bookworm as opcut-base
WORKDIR /opcut
RUN apt update -y && \
    apt install -y pkg-config gcc libcairo2-dev

FROM opcut-base as opcut-build
WORKDIR /opcut
RUN apt install -y nodejs yarnpkg git  && \
    ln -sT /usr/bin/yarnpkg /usr/bin/yarn
COPY . .
RUN pip install -r requirements.pip.txt && \
    doit clean_all && \
    doit

FROM opcut-base as opcut-run
WORKDIR /opcut
COPY --from=opcut-build /opcut/build/py/*.whl .
RUN pip install *.whl && \
    rm *.whl
EXPOSE 8080
CMD ["/usr/local/bin/opcut", "server"]
