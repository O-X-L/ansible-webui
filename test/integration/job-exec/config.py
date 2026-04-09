from os import environ

BASE_URL = 'http://127.0.0.1:8000/api'
API_USER = environ['AW_ADMIN']
API_KEY = environ['AW_API_KEY']
AW_EXECUTOR = 'ansible-runner' if environ.get('AW_EXECUTOR', '0') == '0' else 'oxl-ansible-executor'
SINGLE_TIMEOUT = 10
SCHEDULED_TIMEOUT = 70 + SINGLE_TIMEOUT  # time to start the thread & cron-job wait-time (1m)
