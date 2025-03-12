from aw.model.job import JobExecution, JobQueue
from aw.utils.debug import log


def queue_get() -> (JobExecution, None):
    next_queue_item = JobQueue.objects.order_by('-created').first()
    if next_queue_item is None:
        return None

    execution = next_queue_item.execution
    next_queue_item.delete()
    return execution


def queue_add(execution):
    log(msg=f"Job '{execution.job.name} {execution.id}' added to execution queue", level=4)
    JobQueue(execution=execution).save()
