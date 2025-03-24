from os import environ
from time import sleep

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import chromedriver_autoinstaller

# pylint: disable=R0801

BASE_URL = 'http://127.0.0.1:8000'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--disable-logging')
options.add_argument('--log-level=3')
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--enable-javascript')
chromedriver_autoinstaller.install()
DRIVER = webdriver.Chrome(options=options)


def _get_requests(url: str) -> dict:
    reqs = {'main': None, 'sub': []}

    if url.find('#') != -1:
        url = url.split('#', 1)[0]

    for r in DRIVER.requests:
        if not r.response or r.url.endswith('favicon.ico') or \
                r.url.find('google') != -1 or \
                r.url.find('chrome_component') != -1 or \
                r.url.find('chromewebstore') != -1:
            continue

        print(f" > {r.url.replace(BASE_URL, '')}")
        if r.url == url:
            reqs['main'] = r

        elif r.url.startswith(BASE_URL) and r.headers['Referer'] == url:
            reqs['sub'].append(r)

    del DRIVER.requests
    return reqs


def _check_requests(url: str, sub: bool = False) -> bool:
    reqs = _get_requests(url)
    if not sub:
        if reqs['main'] is None:
            print(f"ERROR: No direct request to URL found: '{reqs}'")
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


def _wait_for_load():
    WebDriverWait(
        DRIVER, 5.0, 0.2,
    ).until(expected_conditions.presence_of_element_located((By.ID, 'loaded')))


def _open_and_wait_for_load(url: str):
    DRIVER.get(url)
    _wait_for_load()


def login_fallback(user: str, pwd: str):
    print('TESTING FALLBACK-LOGIN')
    url = f'{BASE_URL}/a/login/fallback/'
    _open_and_wait_for_load(url)

    DRIVER.find_element(By.ID, 'id_username').send_keys(user)
    DRIVER.find_element(By.ID, 'id_password').send_keys(pwd)
    DRIVER.find_element(By.ID, 'id_password').send_keys(Keys.RETURN)

    assert _check_requests(url)
    assert _check_console_logs(url)

    login_redirect = f'{BASE_URL}/ui#dashboard'
    assert DRIVER.current_url == login_redirect


def test_get_locations(to_check: dict):
    for location, tab_fragment in to_check.items():
        print(f'TESTING GET /{location}')
        url = f'{BASE_URL}/{location}'
        _open_and_wait_for_load(url)

        assert _check_requests(url)
        assert _check_console_logs(url)

        for tab_class, fragment in tab_fragment.items():
            print(f'TESTING GET /{location}{fragment}')
            DRIVER.find_element(By.CLASS_NAME, tab_class).click()
            _wait_for_load()
            sleep(2)  # wait for JS async fetches (in case they would fail)

            assert _check_requests(url, sub=True)
            assert _check_console_logs(url)


def test_auth_pages():
    test_get_locations({
        'a/login/': {},
        'a/login/fallback/': {},
    })


def test_fallback_main_pages():
    test_get_locations({
        'ui': {
            'tab-jobs': '#jobs',
            'tab-logs': '#logs',
            'tab-repositories': '#repositories',
            'tab-credentials': '#credentials',
            'tab-dashboard': '#dashboard',
        },
        'ui/system': {
            'tab-admin': '#admin',
            'tab-settings': '#settings',
        },
    })


def main():
    try:
        test_auth_pages()
        login_fallback(user=environ['AW_ADMIN'], pwd=environ['AW_ADMIN_PWD'])
        test_fallback_main_pages()

    finally:
        DRIVER.quit()


if __name__ == '__main__':
    main()
