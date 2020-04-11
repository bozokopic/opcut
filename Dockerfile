FROM python:3.8-buster AS base


FROM base AS build

RUN apt-get update \
    && apt-get install -q -y nodejs yarnpkg \
    && ln -s /usr/bin/yarnpkg /usr/bin/yarn

COPY . /opcut

RUN cd /opcut \
    && pip install -r requirements.txt \
    && doit


FROM base AS run

COPY --from=build /opcut/dist /opcut/dist

RUN pip install /opcut/dist/*

EXPOSE 80

CMD ["opcut", "server", "--addr", "http://0.0.0.0:80"]
