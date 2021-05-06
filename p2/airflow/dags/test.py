from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

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

TASKS = [
    {
        'id': 'create_dir',
        'type': BashOperator,
        'params': {
            'bash_command': 'mkdir -p /tmp/test/',
            'depends_on_past': False
        },
    },
    {
        'id': 'create_file',
        'type': BashOperator,
        'params': {
            'bash_command': 'touch /tmp/test/xd.txt',
            'depends_on_past': True
        }
    },
    {
        'parallel': [
            {
                'id': 'create_dir123',
                'type': BashOperator,
                'params': {
                    'bash_command': 'mkdir -p /tmp/test/123',
                    'depends_on_past': False
                },
            },
            {
                'id': 'create_dir456',
                'type': BashOperator,
                'params': {
                    'bash_command': 'mkdir -p /tmp/test/456',
                    'depends_on_past': False
                },
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
    dag_id = 'test',
    default_args = DEFAULT_ARGS,
    description = 'Dag test',
    dagrun_timeout = timedelta(minutes=2),
    schedule_interval = timedelta(days=1),
)

generate_operators(dag, TASKS)