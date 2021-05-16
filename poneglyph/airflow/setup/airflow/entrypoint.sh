#!/usr/bin/env bash

export AIRFLOW_HOME=/usr/local/airflow
export AIRFLOW__CORE__LOAD_EXAMPLES=False

git init /usr/local/airflow

airflow db init

airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email spiderman@superhero.org \
    --password admin

airflow scheduler &>/dev/null &

exec airflow webserver

