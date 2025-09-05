from celery import Celery

# Create a Celery instance
# The first argument is the name of the current module, which is 'celery_app'
# The 'broker' argument specifies the URL of the message broker to use (Redis in this case)
# The 'backend' argument specifies the result backend to use (also Redis)
celery_app = Celery(
    'celery_app',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

# Import tasks directly to ensure they are registered
import tasks

# Optional configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start()
