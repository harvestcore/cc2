from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

from dotenv import dotenv_values

ENV_PATH = '.env'
config = dotenv_values(ENV_PATH)

def compute_operator(dag, operator):
    if 'parallel' in operator:
        return [
            compute_operator(dag, op) for op in operator['parallel']
        ]

    params = {
        'dag': dag,
        'task_id': operator['id']
    }
    params.update(operator['params'])

    return operator['type'](**params)

def generate_operators(dag, tasks):
    n_tasks = len(tasks)

    if n_tasks == 0:
        return
    elif n_tasks == 1:
        return compute_operator(dag, tasks[0])
    else:
        flow = compute_operator(dag, tasks[0])

        # Remove first computed operator
        del tasks[0]

        for operator in tasks:
            flow = flow >> compute_operator(dag, operator)
        return flow

### Python operator callables

def check_python_dependencies():
    import subprocess
    import sys
    dependencies = ['pandas', 'pytest', 'pymongo', 'urllib']

    for dep in dependencies:
        try:
            exec(f"import {dep}")
        except:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                dep
            ])

def process_csv():
    import pandas as pd

    temperature = pd.read_csv(
        '/p2/csv/data/temperature.csv',
        header=0
    )
    
    humidity = pd.read_csv(
        '/p2/csv/data/humidity.csv',
        header=0
    )

    frame = pd.DataFrame(data={
        'DATE': temperature['datetime'],
        'TEMP': temperature['San Francisco'],
        'HUM': humidity['San Francisco']
    })

    frame.to_csv(
        '/p2/csv/data/san_francisco.csv',
        sep=',',
        encoding='utf-8',
        index=False
    )

def save_data_to_mongo():
    import pandas as pd
    import pymongo

    sf = pd.read_csv(
        '/p2/csv/data/san_francisco.csv',
        header=0
    )

    client = pymongo.MongoClient(config['MONGO_URI'])
    db = client.data['san-francisco'].insert_many(sf.to_dict())


TASKS = [
    {
        'id': 'check_python_dependencies',
        'type': PythonOperator,
        'params': {
            'python_callable': check_python_dependencies
        }
    },
    {
        'id': 'check_ubuntu_dependencies',
        'type': BashOperator,
        'params': {
            'bash_command': 'apt install unzip'
        }
    },
    {
        'id': 'create_root_folder',
        'type': BashOperator,
        'params': {
            'bash_command': 'touch /p2'
        }
    },
    {
        'id': 'download_csv_data',
        'type': BashOperator,
        'params': {
            'bash_command': '\
                wget -p /p2/csv https://github.com/manuparra/MaterialCC2020/blob/master/humidity.csv.zip && \
                wget -p /p2/csv https://github.com/manuparra/MaterialCC2020/blob/master/temperature.csv.zip'
        }
    },
    {
        'id': 'unzip_csv_data',
        'type': BashOperator,
        'params': {
            'bash_command': '\
                unzip /p2/csv/humidity.csv.zip && \
                unzip /p2/csv/temperature.csv.zip && \
                rm -rf *.zip'
        }
    },
    {
        'id': 'download_repo',
        'type': BashOperator,
        'params': {
            'bash_command': '\
                wget -p /p2 https://github.com/harvestcore/cc2/archive/refs/heads/develop.zip && \
                unzip /p2/develop.zip && \
                mv cc2-develop/p2/api . && \
                rm -rf *.zip'
        }
    },
    {
        'id': 'process_csv',
        'type': PythonOperator,
        'params': {
            'python_callable': process_csv
        }
    },
    {
        'id': 'save_data_to_mongo',
        'type': PythonOperator,
        'params': {
            'python_callable': save_data_to_mongo
        }
    },
    {
        'parallel': [
            {
                'id': 'test_api_v1',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        cd /p2/api/v1 && \
                        python -m pip install -r requirements.txt && \
                        python -m pytest'
                }
            },
            {
                'id': 'test_api_v2',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        cd /p2/api/v2 && \
                        python -m pip install -r requirements.txt && \
                        python -m pytest'
                }
            }
        ]
    },
    {
        'id': 'echo_check',
        'type': BashOperator,
        'params': {
            'bash_command': 'echo "Still alive"'
        }
    },
    {
        'parallel': [
            {
                'id': 'deploy_api_v1',
                'type': BashOperator,
                'params': {
                    'bash_command': 'echo "TODO"'
                }
            },
            {
                'id': 'deploy_api_v2',
                'type': BashOperator,
                'params': {
                    'bash_command': 'echo "TODO"'
                }
            }
        ]
    }
]

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    dag_id = 'deploy_v1_v2',
    default_args = DEFAULT_ARGS,
    description = 'Deploy API v1 and v2',
    dagrun_timeout = timedelta(minutes=2),
    schedule_interval = timedelta(days=1),
)

generate_operators(dag, TASKS)
