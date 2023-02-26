import travel.parsing.travelata as travelata
from travel.utils import safe_mkdir
import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(
    dag_id="etl_travelata_from_html",
    schedule=None,
    catchup=False,
    schedule_interval=None,
    start_date=datetime.datetime(1970, 1, 1),
) as dag:
    parse_travelata_task = PythonOperator(
        task_id="parse_travelate_html", python_callable=travelata.parse_html,
        dag=dag, op_kwargs={
            "pattern_html": "data_html/collected_hotels_*.html",
            "output_file": "./data/results/result_travelata_raw.json"
        }
    )
    safe_mkdir("./data/results")

    extract_travelata_task = PythonOperator(
        task_id="extract_travelate_html",
        python_callable=travelata.create_attributes,
        dag=dag, op_kwargs={
            "input_file":  "./data/results/result_travelata_raw.json",
            "output_file":  "./data/results/result_travelata.json"
        }
    )

    parse_travelata_task >> extract_travelata_task
    

    
