from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

"""
    This function generates the individual (or parallel) operators
    to be used in a flow.
    
    It returns the following dictionary, with information
    about the single operator that has been computed.
    
        {
            'operator': Operator[] | Operator,
            'operator_id': str,
            'entities': {}<string, Operator>
        }
    
    Params:
    - dag: The Dag object to be used.
    - operator: The operator to be computed. This operator object has
    the following structure:

        {
            'id': str,          # Operator identifier.
            'type': Operator,   # Operator to be used.
            'params': {}        # Operator specific parameters.
        }
"""
def generate_operator(dag, operator):
    # This operator is parallel.
    if 'parallel' in operator:        
        # Output object.
        output = {
            # List of parallel operators.
            'operator': [],
            # Operator ID, so it can be referenced later.
            'operator_id': operator['id'],
            # Dict containing all the different operators used in this parallel.
            'entities': {}
        }
        
        # Compute all the operators in the parallel.
        for op in operator['parallel']:
            # Compute the operator.
            computed = generate_operator(dag, op)
            # Update the parallel operators list and the entities.
            output['operator'].append(computed['operator'])
            output['entities'].update(computed['entities'])

        return output
    
    # Operator default parameters.
    params = {
        'dag': dag,
        'task_id': operator['id']
    }
    # Update default parameters with individual operator parameters.
    params.update(operator['params'])
    
    # Generate the operator.
    computed_operator = operator['type'](**params)

    # Return operator information.
    return {
        'operator': computed_operator,
        'operator_id': operator['id'],
        'entities': {
            operator['id']: computed_operator
        }
    }

"""
    This function generates a flow by the given tasks.
    
    In this case this function returns the following dictionary,
    with all the related information.
    
        {
            'flow': Operator,   # Generated flow.
            'entities': {}      # All the Operator entities used.
        }
"""
def generate_flow(dag, tasks, dependencies):
    n_tasks = len(tasks)
    
    # There are no tasks, return.
    if n_tasks == 0:
        return
    
    # There is only one task, compute it and return it.
    elif n_tasks == 1:
        computed_operator = generate_operator(dag, tasks[0])
        flow = computed_operator['operator']
        
        if len(dependencies) > 0:
            return {
                'flow': dependencies[0] >> flow,
                'entities': computed_operator['entities']
            }
        
        return {
            'flow': flow,
            'entities': computed_operator['entities']
        }
    else:
        entities = {}
        generated_operator = generate_operator(dag, tasks[0])
        flow = generated_operator['operator']
        
        if len(dependencies) > 0:
            flow = dependencies[0] >> flow
            
        entities.update(generated_operator['entities'])
                
        del tasks[0]
        
        for operator in tasks:
            generated_operator = generate_operator(dag, operator)
            entities.update(generated_operator['entities'])
            flow = flow >> generated_operator['operator']
            
        return {
            'flow': flow,
            'entities': entities
        }

"""
    This function generates the airflow flows.
"""
def generate_airflows(dag, flows):
    n_flows = len(flows)

    if n_flows == 0:
        yield None
    elif n_flows == 1:
        generated_flow = generate_flow(dag, flows[0], [])
        yield generated_flow['flow']
    else:
        entities = {}
        generated_flows = []

        for flow in flows:
            dependencies = []
            if 'depends_on' in flow:
                dependencies.append(entities[flow['depends_on']])
            
            generated_flow = generate_flow(dag, flow['tasks'], dependencies)
            current_flow = generated_flow['flow']
            entities.update(generated_flow['entities'])


            yield current_flow

### Python operator callables

def check_python_dependencies():
    import subprocess
    import sys
    dependencies = ['pandas', 'pytest', 'pymongo', 'zipfile', 'urllib']

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
        '/tmp/p2/csv/temperature.csv',
        header=0
    )
    
    humidity = pd.read_csv(
        '/tmp/p2/csv/humidity.csv',
        header=0
    )

    frame = pd.DataFrame(data={
        'DATE': temperature['datetime'],
        'TEMP': temperature['San Francisco'],
        'HUM': humidity['San Francisco']
    })

    frame.to_csv(
        '/tmp/p2/mongo/sanfrancisco.csv',
        sep=',',
        encoding='utf-8',
        index=False
    )

def extract_data():
    import zipfile
    
    with zipfile.ZipFile('/tmp/p2/csv/humidity.csv.zip', 'r') as humidity_zip:
        humidity_zip.extractall('/tmp/p2/csv/')

    with zipfile.ZipFile('/tmp/p2/csv/temperature.csv.zip', 'r') as temperature_zip:
        temperature_zip.extractall('/tmp/p2/csv/')

def extract_repo():
    import zipfile
    
    with zipfile.ZipFile('/tmp/p2/cc2.zip', 'r') as repo:
        repo.extractall('/tmp/p2/')

FLOWS = [
    {
        'flow_id': 'check_dependencies',
        'tasks': [
            {
                'id': 'check_python_dependencies',
                'type': PythonOperator,
                'params': {
                    'python_callable': check_python_dependencies
                }
            },
            {
                'id': 'create_root_folder',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        mkdir /tmp/p2 && \
                        mkdir /tmp/p2/csv'
                }
            }
        ]
    },
    {
        'flow_id': 'download_data',
        'depends_on': 'create_root_folder',
        'tasks': [
            {
                'id': 'download_csv_data',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        cd /tmp/p2/csv && \
                        curl -o /tmp/p2/csv/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip && \
                        curl -o /tmp/p2/csv/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip'
                }
            },
            {
                'id': 'show_folder',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        cd /tmp/p2/csv && \
                        ls -lah'
                }
            },
            {
                'id': 'unzip_csv_data',
                'type': PythonOperator,
                'params': {
                    'python_callable': extract_data
                }
            },
            {
                'id': 'download_repo',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        cd /tmp/p2 && \
                        curl -o /tmp/p2/cc2.zip -LJ https://github.com/harvestcore/cc2/archive/refs/heads/develop.zip'
                }
            },
            {
                'id': 'extract_repo',
                'type': PythonOperator,
                'params': {
                    'python_callable': extract_repo
                }
            },
            {
                'id': 'extract_apis',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        cd /tmp/p2 && \
                        ls -lah && \
                        mv cc2-develop/p2/api . && \
                        mv cc2-develop/p2/mongo .'
                }
            }
        ]
    },
    {
        'flow_id': 'process_data',
        'depends_on': 'extract_apis',
        'tasks': [
            {
                'id': 'process_csv',
                'type': PythonOperator,
                'params': {
                    'python_callable': process_csv
                }
            },
            {
                'id': 'build_mongo_database',
                'type': BashOperator,
                'params': {
                    'bash_command': '\
                        cd /tmp/p2/mongo && \
                        docker-compose build'
                }
            },
            {
                'id': 'run_mongo_database',
                'type': BashOperator,
                'params': {
                    'bash_command': 'docker-compose up -d'
                }
            }
        ]
    },
    {
        'flow_id': 'test_api',
        'depends_on': 'run_mongo_database',
        'tasks': [
            {
                'id': 'parallel_test_api',
                'parallel': [
                    {
                        'id': 'test_api_v1',
                        'type': BashOperator,
                        'params': {
                            'bash_command': '\
                                cd /tmp/p2/api/v1 && \
                                python3 -m pip install -r requirements.txt && \
                                python3 -m pytest'
                        }
                    },
                    {
                        'id': 'test_api_v2',
                        'type': BashOperator,
                        'params': {
                            'bash_command': '\
                                cd /tmp/p2/api/v2 && \
                                python3 -m pip install -r requirements.txt && \
                                python3 -m pytest'
                        }
                    }
                ]
            }
        ]
    },
    {
        'flow_id': 'deploy_api_v1',
        'depends_on': 'test_api_v1',
        'tasks': [
            {
                'id': 'train_api_v1_data',
                'type': BashOperator,
                'params': {
                    'bash_command': 'python3 train.py'
                }
            },
            {
                'id': 'build_image_api_v1',
                'type': BashOperator,
                'params': {
                    'bash_command': 'docker-compose build'
                }
            },
            {
                'id': 'run_image_api_v1',
                'type': BashOperator,
                'params': {
                    'bash_command': 'docker-compose up -d'
                }
            }
        ]
    },
    {
        'flow_id': 'deploy_api_v2',
        'depends_on': 'test_api_v2',
        'tasks': [
            {
                'id': 'build_image_api_v2',
                'type': BashOperator,
                'params': {
                    'bash_command': 'docker-compose build'
                }
            },
            {
                'id': 'run_image_api_v2',
                'type': BashOperator,
                'params': {
                    'bash_command': 'docker-compose up -d'
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

out = generate_airflows(dag, FLOWS)

for flow in out:
    next(out)
