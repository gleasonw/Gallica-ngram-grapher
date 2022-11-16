from celery import Celery
import time
from appsearch.request import buildRequest
from database.connContext import build_db_conn

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawn_request(self, tickets, request_id):
    with build_db_conn() as conn:
        request = buildRequest(
            argsBundles=tickets,
            identifier=request_id,
            conn=conn
        )
        request.start()
        poll_state_router = {
            'RUNNING': lambda: self.update_state(
                state='RUNNING',
                meta={'progress': request.getProgressStats()}
            ),
            'ADDING_MISSING_PAPERS': lambda: self.update_state(
                state='ADDING_MISSING_PAPERS',
                meta={'progress': request.getProgressStats()}
            ),
            'ADDING_RESULTS': lambda: self.update_state(
                state='ADDING_RESULTS',
                meta={'progress': request.getProgressStats()}
            )
        }
        while True:
            if poll_state_action := poll_state_router.get(request.state):
                poll_state_action()
            else:
                return {
                    'state': request.state,
                    'numRecords': request.estimateNumRecords
                }
            time.sleep(1)

