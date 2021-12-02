import sys, time

from mlflow_client import MLflowClient
from mlflow_client.log import get_logger
from mlflow_client.timestamp import current_timestamp

logger = get_logger()


def process(client):
    logger.info("====== list_experiments")
    exps = client.list_experiments()
    logger.info("list_experiments: #experiments: {}".format(len(exps)))
    for exp in exps:
        logger.info("  {}".format(exp))

    logger.info("====== get_or_create_experiment")
    experiment_name = "py_exp_" + str(time.time()).replace(".", "")
    logger.info("create experiment with name {}".format(experiment_name))
    experiment = client.get_or_create_experiment(experiment_name)
    logger.info("  id: {}".format(experiment.id))

    logger.info("====== create_run")
    run_name = "run_for_exp_" + experiment_name
    start_time = current_timestamp()
    run = client.create_run(experiment_id=experiment.id, name=run_name, start_time=start_time)
    logger.info("  run id {}".format(run.id))

    logger.info("====== log_run_parameter and metrics")
    param_key = "max_depth"
    param_value = "2"
    client.log_run_parameter(run.id, param_key, param_value)

    logger.info("====== log_run_metric")
    metric_key = "auc"
    metric_value = 0.59
    client.log_run_metric(run.id, metric_key, metric_value)
    metric_value = 0.69
    client.log_run_metric(run.id, metric_key, metric_value, step=1, timestamp=start_time + 10)
    metric_value = 0.79
    client.log_run_metric(run.id, metric_key, metric_value, step=2, timestamp=start_time + 15)
    metric_value = 0.89
    client.log_run_metric(run.id, metric_key, metric_value, step=2, timestamp=start_time + 20)
    metric_value = 0.99
    client.log_run_metric(run.id, metric_key, metric_value, step=3, timestamp=start_time + 30)

    logger.info("====== finish_run")
    client.finish_run(run.id, end_time=start_time + 20)

    logger.info("====== get_run")
    run = client.get_run(run.id)
    logger.info("  {}".format(run))

    logger.info("====== get_experiment")
    experiment = client.get_experiment(experiment.id)
    logger.info("  {}".format(experiment))

    logger.info("====== get_metric_history")
    metric_history = client.get_run_metric_history(run.id, metric_key)
    logger.info("  {}".format(metric_history))

    logger.info("====== list_run_artifacts")
    artifacts = client.list_run_artifacts(run.id)
    logger.info("  {}".format(artifacts))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: Expecting BASE_URL")
        sys.exit(1)
    client = MLflowClient(sys.argv[1])
    process(client)
