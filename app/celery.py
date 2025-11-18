from celery import Celery
import time

app = Celery('сelery', broker='redis://localhost:6379')

@app.task
def add(x, y):
    time.sleep(30)
    return x + y