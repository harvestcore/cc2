from time import *

import pyspark.sql.functions as functions
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.tuning import TrainValidationSplit, ParamGridBuilder
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.classification import GBTClassifier, RandomForestClassifier, NaiveBayes, LogisticRegression


TRAINING_PORTION = 0.75

def run_classification_algorithm(name, params):
    if name in ['random_forest', 'naive_bayes', 'logistic_regresion', 'gradient_boosted_tree']:
        tic = time()
        output = globals()[name](params)
        toc = time()
        
        output.update({ 'time': round((toc - tic), 2) })
        return output
    
def __evaluate_algorithm(estimator, params, training, testing):
    training_validator = TrainValidationSplit(
        estimator=estimator,
        estimatorParamMaps=params,
        evaluator=BinaryClassificationEvaluator(),
        trainRatio=TRAINING_PORTION
    )
    model = training_validator.fit(training)
    
    predictions = model.transform(testing)
    subset = predictions.select("prediction", "label")

    # Cast labels and predictions to float.
    subset = subset.withColumn(
        "prediction",
        functions.round(subset['prediction']).cast('float')
    )
    subset = subset.withColumn(
        "label",
        functions.round(subset['label']).cast('float')
    )
    
    # Get some metrics.
    metrics = MulticlassMetrics(subset.select("prediction", "label").rdd.map(tuple))
    
    # Get the AUC value.
    evaluator = BinaryClassificationEvaluator()
    auc = evaluator.evaluate(predictions)

    return {
        'predictions': predictions,
        'model': model,
        'auc': auc,
        'accuracy': metrics.accuracy,
        'metrics': metrics
    }

def random_forest(params):
    _random_forest = RandomForestClassifier(
        labelCol="label",
        featuresCol="features",
        seed=params['seed']
    )
    
    params_grid = ParamGridBuilder().addGrid(
        _random_forest.numTrees, params['trees']
    ).addGrid(
        _random_forest.maxDepth, params['depth']
    ).build()
    
    return __evaluate_algorithm(
        _random_forest,
        params_grid,
        params['training'],
        params['testing']
    )
    
def naive_bayes(params):
    _naive_bayes = NaiveBayes(
        modelType="multinomial",
        featuresCol="features",
        labelCol="label",
        smoothing=params['smoothing']
    )
    
    grid = ParamGridBuilder().addGrid(
        _naive_bayes.smoothing,
        params['grid']
    ).build()
    
    return __evaluate_algorithm(
        _naive_bayes,
        grid,
        params['training'],
        params['testing']
    )
    
def logistic_regresion(params):
    _logistic_regresion = LogisticRegression(
        featuresCol="features",
        labelCol="label",
        maxIter=params['iterations'],
        family="multinomial"
    )
    
    grid = ParamGridBuilder().addGrid(
        _logistic_regresion.regParam, params['reg']
    ).addGrid(
        _logistic_regresion.elasticNetParam, params['elastic_net']
    ).build()
    
    return __evaluate_algorithm(
        _logistic_regresion,
        grid,
        params['training'],
        params['testing']
    )
    
def gradient_boosted_tree(params):
    _gradient_boosted_tree = GBTClassifier(
        labelCol="label",
        featuresCol="features",
        seed=params['seed']
    )

    grid = ParamGridBuilder().addGrid(
        _gradient_boosted_tree.maxIter, params['iter']
    ).addGrid(
        _gradient_boosted_tree.maxDepth, params['depth']
    ).build()
    
    return __evaluate_algorithm(
        _gradient_boosted_tree,
        grid,
        params['training'],
        params['testing']
    )
