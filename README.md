**Projekt DIH4CPS**

***Getting Started:***\n
    *Step 1: setup virtual environment*
        - Linux: (need to be tested)
            python -m venv .linux_venv
            source .linux_venv/bin/activate
            pip install -r requirements.txt 
        - Windows (Visual Studio Code):
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
            py -3 -m venv .venv
            .\.venv\Scripts\activate 
            pip install -r requirements.txt 
            __
    *Step 2: setup crontabs to run the program*
        - Linux: 
            python3 cron_handler.py
            --> make sure cron_handler is using the python path of the created venv 
        - Windows:
            setup cronjobs manually (Task Scheduler)
            --> make sure cron_handler is using the python path of the created venv 
