from global_variables import get_job_queue

if __name__ == "__main__":
    job = "record,frames=60"
    print(job)
    get_job_queue().put(job)