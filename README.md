**Projekt DIH4CPS**\
***Getting Started:***\
\
    *Step 1: setup virtual environment*\
    \
      - Linux: (need to be tested)\
&nbsp;&nbsp; python -m venv .linux_venv\
&nbsp;&nbsp; source .linux_venv/bin/activate\
&nbsp;&nbsp; pip install -r requirements.txt\
        - Windows (Visual Studio Code):\
&nbsp;&nbsp; Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process\
&nbsp;&nbsp; py -3 -m venv .venv \
&nbsp;&nbsp; .\.venv\Scripts\activate \
&nbsp;&nbsp; pip install -r requirements.txt\
            \
    *Step 2: setup crontabs to run the program* \
    \
        - Linux: \
&nbsp;&nbsp; python3 cron_handler.py \
&nbsp;&nbsp; --> make sure cron_handler is using the python path of the created venv\
        - Windows: \
&nbsp;&nbsp; setup cronjobs manually (Task Scheduler)\
&nbsp;&nbsp; --> make sure cron_handler is using the python path of the created venv
