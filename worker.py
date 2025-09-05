from celery_app import celery_app
# This import is necessary so that the worker discovers the task
from tasks import analyze_episode

if __name__ == '__main__':
    # This is not strictly necessary for the Docker container,
    # but it allows running the worker directly for development/debugging.
    # The command-line arguments for Celery will be passed when this script is executed.
    celery_app.worker_main()
