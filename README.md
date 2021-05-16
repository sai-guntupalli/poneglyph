
## create python env
conda create -n poneglypgh python=3.8

## install airflow

pip install "apache-airflow==2.0.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.0.1/constraints-3.8.txt"

pip install -r requirements.txt

.