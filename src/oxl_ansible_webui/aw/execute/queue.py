from aw.model.job import JobExecution, JobQueue
from aw.utils.debug import log, log_security
from aw.utils.crypto import decrypt, encrypt

from aw.utils.db_handler import close_old_mysql_connections

def queue_get() -> (JobExecution, None):
    close_old_mysql_connections()
    next_queue_item = JobQueue.objects.order_by('-created').first()
    if next_queue_item is None:
        return None

    execution = next_queue_item.execution
    v = next_queue_item.v
    next_queue_item.delete()

    if decrypt(v) != str(execution):
        log_security(f"Job '{execution.job.name} {execution.id}' failed execution queue validation - possible attack")
        return None

    return execution


def queue_add(execution: JobExecution):
    log(msg=f"Job '{execution.job.name} {execution.id}' added to execution queue", level=4)
    q = JobQueue(execution=execution, v=encrypt(str(execution)))
    close_old_mysql_connections()
    q.save()
