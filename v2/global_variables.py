import queue

global global_job_queue
global_job_queue = queue.Queue()

def get_job_queue():
    return global_job_queue