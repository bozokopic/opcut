FROM python:3.10-slim-bullseye as opcut-base
WORKDIR /opcut
RUN apt update -qy && \
    apt install -qy pkg-config gcc libcairo2-dev

FROM opcut-base as opcut-build
WORKDIR /opcut
RUN apt install -qy nodejs yarnpkg git gcc-mingw-w64-x86-64-win32 && \
    ln -sT /usr/bin/yarnpkg /usr/bin/yarn && \
    ln -sT /usr/bin/x86_64-w64-mingw32-gcc /usr/bin/x86_64-w64-mingw32-cc
COPY . .
RUN pip install -qq -r requirements.pip.dev.txt && \
    doit clean_all && \
    doit

FROM opcut-base as opcut-run
WORKDIR /opcut
COPY --from=opcut-build /opcut/build/py/dist/*.whl .
RUN pip install -qq *.whl && \
    rm *.whl
EXPOSE 8080
CMD ["/usr/local/bin/opcut", "server"]
