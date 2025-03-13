from os import environ
from time import sleep

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

# pylint: disable=R0801

BASE_URL = 'http://127.0.0.1:8000'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--disable-logging')
options.add_argument('--log-level=3')
options.add_argument('--remote-debugging-port=9222')
chromedriver_autoinstaller.install()
DRIVER = webdriver.Chrome(options=options)


def _get_requests(url: str) -> dict:
    reqs = {'main': None, 'sub': []}

    for r in DRIVER.requests:
        if not r.response or r.url.endswith('favicon.ico'):
            continue

        if r.url == url:
            reqs['main'] = r

        elif r.url.startswith(BASE_URL) and r.headers['Referer'] == url:
            reqs['sub'].append(r)

    del DRIVER.requests
    return reqs


def _check_requests(url: str) -> bool:
    reqs = _get_requests(url)
    if reqs['main'] is None:
        return False

    sc = reqs['main'].response.status_code
    if sc not in [200, 302]:
        print(f"ERROR: Bad response-code {sc} @ '{reqs['main']}'")
        return False

    for sr in reqs['sub']:
        sc = sr.response.status_code
        if sc not in [200, 304]:
            print(f"ERROR: Bad response-code {sc} @ '{sr}'")
            return False

    return True


def _check_console_logs(url: str) -> bool:
    errors = []
    for log in DRIVER.get_log('browser'):
        if log['level'] == 'SEVERE':
            errors.append(log)

    if len(errors) > 0:
        print(f"ERROR: Issue(s) in logs/console @ '{url}'")
        print('\n'.join([f"{e['level']} {e['source']}: \"{e['message']}\"" for e in errors]))
        return False

    return True


def _response_ok(url: str) -> bool:
    return _check_requests(url) and _check_console_logs(url)


def login(user: str, pwd: str):
    print('TESTING LOGIN')
    login_url = f'{BASE_URL}/a/login/'
    DRIVER.get(login_url)
    DRIVER.find_element(By.ID, 'id_username').send_keys(user)
    DRIVER.find_element(By.ID, 'id_password').send_keys(pwd)
    DRIVER.find_element(By.ID, 'id_password').send_keys(Keys.RETURN)
    assert _response_ok(login_url)

    login_redirect = f'{BASE_URL}/ui/jobs/manage'
    assert DRIVER.current_url == login_redirect


def test_get_locations(locations: list):
    for location in locations:
        print(f'TESTING GET {location}')
        url = f'{BASE_URL}/{location}'
        sleep(0.05)
        DRIVER.get(url)
        assert _response_ok(url)


def test_main_pages():
    test_get_locations([
        'ui/jobs/manage', 'ui/jobs/log', 'ui/jobs/credentials', 'ui/jobs/repository',
        'ui/settings/api_keys', 'ui/settings/permissions',
        'ui/system/admin/', 'ui/system/api_docs', 'ui/system/environment',
        # 'ui/system/config',
        'a/password_change/', 'ui/settings/alerts',
    ])


# todo: update form-checks after frontend refactor
# todo: check for JS errors

def test_actions_views():
    test_get_locations([
        # 'ui/jobs/manage/job',
        # 'ui/jobs/credentials/0?global=false', 'ui/jobs/credentials/0?global=true',
        # 'ui/settings/permissions/0', 'ui/jobs/repository/git/0', 'ui/jobs/repository/static/0',
        # 'ui/settings/alerts/global/0', 'ui/settings/alerts/group/0', 'ui/settings/alerts/user/0',
        # 'ui/settings/alerts/plugin/0',
    ])


def main():
    try:
        login(user=environ['AW_ADMIN'], pwd=environ['AW_ADMIN_PWD'])
        test_main_pages()
        # test_actions_views()
        # todo: add action post variants

    finally:
        DRIVER.quit()


if __name__ == '__main__':
    main()
