from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 14),
    'email': ['example@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('census_data_pipeline',
          default_args=default_args,
          description='A simple DAG to process census data',
          schedule=timedelta(days=1))

def download_data():
    url = "https://raw.githubusercontent.com/practical-bootcamp/week4-assignment1-template/main/city_census.csv"
    df = pd.read_csv(url)
    df.to_csv('/home/jithish/Documents/dag-dag-dag/airflow/dags/city_census.csv', index=False)

download_task = PythonOperator(
    task_id='download_data',
    python_callable=download_data,
    dag=dag)

def clean_and_process_data():
    df = pd.read_csv('/home/jithish/Documents/dag-dag-dag/airflow/dags/city_census.csv')
    # Handle missing values
    df.fillna(method='ffill', inplace=True)
    # Filter data (Example: Only data where 'Population' > 100000)
    filtered_df = df[df['weight'] > 200]
    filtered_df.to_csv('/home/jithish/Documents/dag-dag-dag/airflow/dags/filtered_city_census.csv', index=False)

process_task = PythonOperator(
    task_id='process_data',
    python_callable=clean_and_process_data,
    dag=dag)

def store_data():
    engine = create_engine('sqlite:///census_data.db')
    df = pd.read_csv('/home/jithish/Documents/dag-dag-dag/airflow/dags/filtered_city_census.csv')
    df.to_sql('census_data', con=engine, if_exists='replace', index=False)

store_task = PythonOperator(
    task_id='store_data',
    python_callable=store_data,
    dag=dag)

download_task >> process_task >> store_task
