from camunda.external_task.client import ExternalTaskClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Camunda configuration
CAMUNDA_REST_URL = getattr(settings, 'CAMUNDA_REST_URL', 'http://localhost:8080/engine-rest')
CAMUNDA_CLIENT_ID = getattr(settings, 'CAMUNDA_CLIENT_ID', 'phantom-worker')
CAMUNDA_CLIENT_MAX_TASKS = getattr(settings, 'CAMUNDA_CLIENT_MAX_TASKS', 1)
CAMUNDA_CLIENT_LOCK_DURATION = getattr(settings, 'CAMUNDA_CLIENT_LOCK_DURATION', 10000)  # 10 seconds
CAMUNDA_CLIENT_ASYNC_RESPONSE_TIMEOUT = getattr(settings, 'CAMUNDA_CLIENT_ASYNC_RESPONSE_TIMEOUT', 5000)  # 5 seconds

def get_camunda_client():
    """
    Creates and returns a configured Camunda External Task Client
    """
    client = ExternalTaskClient(
        worker_id=CAMUNDA_CLIENT_ID,
        base_url=CAMUNDA_REST_URL,
        max_tasks=CAMUNDA_CLIENT_MAX_TASKS,
        lock_duration=CAMUNDA_CLIENT_LOCK_DURATION,
        async_response_timeout=CAMUNDA_CLIENT_ASYNC_RESPONSE_TIMEOUT
    )
    return client

def handle_camunda_error(task, message, details=None):
    """
    Handles Camunda task errors in a consistent way
    """
    logger.error(f"Camunda task error: {message}", extra={
        'task_id': task.get_task_id(),
        'details': details
    })
    task.error(error_message=message, error_details=str(details) if details else None)

def complete_task_with_variables(task, variables):
    """
    Completes a Camunda task with the given variables
    """
    try:
        task.complete(variables)
        logger.info(f"Task {task.get_task_id()} completed successfully")
    except Exception as e:
        handle_camunda_error(task, "Failed to complete task", str(e))