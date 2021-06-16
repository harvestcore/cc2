from tabulate import tabulate

from pyspark import SparkContext, SparkConf, sql
from pyspark.ml.feature import StringIndexer, VectorAssembler

from utils import run_classification_algorithm


APP_NAME = "p4-spark"
FOLDER = "/data/csv"
TRAINING_PORTION = 0.75
MAX_DATASET_SIZE = 150000
COLUMNS = ['PSSM_r1_-1_R', 'PSSM_central_0_Q', 'PSSM_r2_-1_C', 'PSSM_r2_-2_R', 'PredSA_r1_-2', 'PSSM_r2_1_E']


def setup_spark():
    config = SparkConf().setAppName(APP_NAME)
    context = SparkContext.getOrCreate(conf=config)
    sql_context = sql.SQLContext(context)
    
    return {
        'config': config,
        'context': context,
        'sql_context': sql_context
    }

def get_datasets():
    sql_context = setup_spark()['sql_context']

    # Load the dataframe.
    dataframe = sql_context.read.csv(
        FOLDER,
        sep=",",
        header=True,
        inferSchema=True
    ).limit(MAX_DATASET_SIZE)
    
    # First column
    first_row = dataframe.first()
        
    for col in COLUMNS:
        if type(first_row[col]) is str:
            indexed_column_name = '{}_indexed'.format(col)
            indexer = StringIndexer(
                inputCol=col,
                outputCol=indexed_column_name
            )
            
            dataframe = indexer.fit(dataframe).transform(dataframe)
            dataframe = dataframe.drop(col)
            dataframe = dataframe.withColumnRenamed(indexed_column_name, col)

    # Count the number of negative and positive values.
    negative_values = dataframe.filter(
        dataframe['class'] == 0
    ).count()
    positive_values = dataframe.filter(
        dataframe['class'] == 1
    ).count()
    
    # Get the minimum value of those.
    partition_size = min(negative_values, positive_values)
    
    # Reduce the dataframe.
    reduced_dataframe_negative_values = dataframe.filter(
        dataframe['class'] == 0
    ).limit(partition_size)
    reduced_dataframe_positive_values = dataframe.filter(
        dataframe['class'] == 1
    ).limit(partition_size)

    # Join both dataframes.
    balanced_dataframe = reduced_dataframe_negative_values.union(reduced_dataframe_positive_values)
    
    # Get training and testing sets.
    training, testing = balanced_dataframe.randomSplit([TRAINING_PORTION, 1 - TRAINING_PORTION])

    assembler = VectorAssembler(
        inputCols=COLUMNS,
        outputCol='features'
    )
    
    # Rename columns.
    training = assembler.transform(training).select("features", "class").withColumnRenamed("class", "label")
    testing = assembler.transform(testing).select("features", "class").withColumnRenamed("class", "label")

    return {
        'training': training,
        'testing': testing
    }

if __name__ == "__main__":
    datasets = get_datasets()
    
    header = ['Algorithm', 'Accuracy', 'AUC', 'Time (s)']
    rows = []
    
    output = run_classification_algorithm(
        'random_forest',
        {
            'training': datasets['training'],
            'testing': datasets['testing'],
            
            'trees': [4, 8, 16],
            'depth': [1, 2, 4],
            'seed': 1
        }
    )
    rows.append(['random_forest', output['accuracy'], output['auc'], output['time']])
        
    output = run_classification_algorithm(
        'random_forest',
        {
            'training': datasets['training'],
            'testing': datasets['testing'],
            
            'trees': [8, 16, 32, 64],
            'depth': [1, 2, 4, 8],
            'seed': 1
        }
    )
    rows.append(['random_forest', output['accuracy'], output['auc'], output['time']])

    output = run_classification_algorithm(
        'logistic_regresion',
        {
            'training': datasets['training'],
            'testing': datasets['testing'],
            
            'reg': [0.1, 0.01, 0.001],
            'elastic_net': [0.2, 0.4, 0.6],
            'iterations': 100
        }
    )
    rows.append(['logistic_regresion', output['accuracy'], output['auc'], output['time']])

    output = run_classification_algorithm(
        'logistic_regresion',
        {
            'training': datasets['training'],
            'testing': datasets['testing'],
            
            'reg': [0.15, 0.015, 0.0015],
            'elastic_net': [0.3, 0.6, 0.9],
            'iterations': 150
        }
    )
    rows.append(['logistic_regresion', output['accuracy'], output['auc'], output['time']])

    output = run_classification_algorithm(
        'gradient_boosted_tree',
        {
            'training': datasets['training'],
            'testing': datasets['testing'],
            
            'iter': [2, 4, 6],
            'depth': [1, 2, 3],
            'seed': 10
        }
    )
    rows.append(['gradient_boosted_tree', output['accuracy'], output['auc'], output['time']])

    output = run_classification_algorithm(
        'gradient_boosted_tree',
        {
            'training': datasets['training'],
            'testing': datasets['testing'],
            
            'iter': [3, 6, 9, 12],
            'depth': [2, 4, 6, 8],
            'seed': 10
        }
    )
    rows.append(['gradient_boosted_tree', output['accuracy'], output['auc'], output['time']])

    # Print results table.
    print(tabulate(rows, header, tablefmt='grid'))
