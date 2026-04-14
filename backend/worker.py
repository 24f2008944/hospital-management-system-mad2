from celery_app import celery
import tasks

if __name__ == '__main__':
    celery.start()
