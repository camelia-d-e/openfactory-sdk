FROM python:3.13-slim-bullseye

ARG UNAME=appuser
ARG UID=1200
ARG GID=1200
ARG VERSION=latest
ARG APPLICATION_MANUFACTURER=test_repo
ARG OPENFACTORY_VERSION=latest

LABEL openfactory.version="${OPENFACTORY_VERSION}" \
      application.version="${VERSION}" \
      source.repository="${APPLICATION_MANUFACTURER}"

RUN adduser --uid ${UID} --disabled-password --gecos "" ${UNAME}

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

RUN if [ "$OPENFACTORY_VERSION" = "latest" ]; then \
      pip install git+https://github.com/Demo-Smart-Factory-Concordia-University/OpenFactory.git ; \
    else \
      pip install git+https://github.com/Demo-Smart-Factory-Concordia-University/OpenFactory.git@$OPENFACTORY_VERSION ; \
    fi

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENV APPLICATION_VERSION=${VERSION}
ENV APPLICATION_MANUFACTURER=${APPLICATION_MANUFACTURER}

WORKDIR /ofa
COPY openfactory_api.py /ofa
RUN chown -R appuser:appuser /ofa

USER ${UNAME}

EXPOSE 8000
CMD ["python3", "-u", "/ofa/openfactory_api.py"]