FROM python:3.8-slim

ARG AIRFLOW_VERSION=2.0.1
ARG PYTHON_VERSION=3.8
ARG AIRFLOW_HOME=/usr/local/airflow

ENV AIRFLOW_HOME=${AIRFLOW_HOME}

RUN apt-get update -yqq && apt-get upgrade -yqq

# RUN apt-get install -yqq --no-install-recommends \
#         freetds-bin \
#         krb5-user \
#         ldap-utils \
#         libffi6 \
#         libsasl2-2 \
#         libsasl2-modules \
#         libssl1.1 \
#         lsb-release \
#         sasl2-bin \
#         sqlite3 \
#         unixodbc \
#         git && apt-get clean

RUN apt-get install -yqq --no-install-recommends \
        build-essential \
        apt-utils \
        gcc \
        vim \
        curl \
        git && apt-get clean

RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

RUN pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

RUN pip install yfinance nsetools pandas dash pymysql

COPY ./entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

RUN vim entrypoint.sh -c "set ff=unix" -c ":wq"

RUN chown -R airflow: ${AIRFLOW_HOME}

USER airflow

WORKDIR ${AIRFLOW_HOME}

ENTRYPOINT [ "/entrypoint.sh" ]