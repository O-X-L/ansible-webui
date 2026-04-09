from os import path as os_path
from sys import path as sys_path

# pylint: disable=R0801,C0413

sys_path.append(os_path.dirname(os_path.abspath(__file__)))

from test_1_simple import test_simple
from test_1p2_execution_cleanup import test_execution_cleanup
from test_2_params import test_params
from test_3_credentials import test_creds
from test_4_repositories import test_repo_git
from test_5_cancel_execution import test_user_cancels
from test_6_scheduled_execution import test_scheduled_execution


def main():
    # Note: job-id's have to be in-order
    test_simple(1)
    test_params(2)
    test_creds(3)
    test_repo_git(4)
    test_user_cancels(5)
    test_scheduled_execution(6)

    test_execution_cleanup(jid=1, exec_id=1)


if __name__ == '__main__':
    main()
