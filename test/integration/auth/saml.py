from os import environ
from time import sleep

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import chromedriver_autoinstaller

# pylint: disable=R0801,R0916

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
    reqs = {'main': None, 'sub': [], 'extern': []}

    if url.find('#') != -1:
        url = url.split('#', 1)[0]

    for r in DRIVER.requests:
        if not r.response or r.url.endswith('favicon.ico') or \
                r.url.find('google') != -1 or \
                r.url.find('gvt1.com') != -1 or \
                r.url.find('chrome_component') != -1 or \
                r.url.find('chromewebstore') != -1:
            continue

        print(f" > {r.url.replace(BASE_URL, '')}")
        if r.url == url:
            reqs['main'] = r

        elif r.url.startswith(BASE_URL) and r.headers['Referer'] == url:
            reqs['sub'].append(r)

        else:
            reqs['extern'].append(r)

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


def _wait_for_load(element_id: str = 'loaded'):
    WebDriverWait(
        DRIVER, 5.0, 0.2,
    ).until(expected_conditions.presence_of_element_located((By.ID, element_id)))


def _open_and_wait_for_load(url: str):
    DRIVER.get(url)
    _wait_for_load()


def _login_base() -> bool:
    url = f'{BASE_URL}/a/login/'
    reqs = _get_requests(url)
    if reqs['main'] is None:
        print(f"ERROR: No direct request to URL found: '{reqs}'")
        return False

    sc = reqs['main'].response.status_code
    if sc not in [200, 302]:
        print(f"ERROR: Bad response-code {sc} @ '{reqs['main']}'")
        return False

    found = {
        'saml_init': False, 'saml_sp': False,
        'idp_sso': False, 'idp_login': False,
    }

    for sr in reqs['sub']:
        if sr.url.find('/a/saml/init/') != -1:
            found['saml_init'] = True

        elif sr.url.find('a/saml/sp/?token=') != -1:
            found['saml_sp'] = True

        sc = sr.response.status_code
        if sc not in [200, 302, 304]:
            print(f"ERROR: Bad response-code {sc} @ '{sr}'")
            return False

    for er in reqs['extern']:
        if er.url.startswith('https://mocksaml.com/api/saml/sso'):
            found['idp_sso'] = True

        elif er.url.startswith('https://mocksaml.com/saml/login'):
            found['idp_login'] = True

    if not DRIVER.current_url.startswith('https://mocksaml.com/saml/login?'):
        return False

    _wait_for_load('username')

    DRIVER.find_element(By.ID, 'username').send_keys('user')
    DRIVER.find_element(By.ID, 'password').send_keys('pwd')
    DRIVER.find_element(By.ID, 'password').send_keys(Keys.RETURN)

    # wait for IDP to redirect us
    sleep(1)
    return True


def login_failure():
    print('TESTING LOGIN FAILURE')
    url = f'{BASE_URL}/a/login/'
    _open_and_wait_for_load(url)

    DRIVER.find_element(By.ID, 'id_username').send_keys('Invalid User')
    DRIVER.find_element(By.ID, 'id_username').send_keys(Keys.RETURN)

    login_redirect = f'{BASE_URL}/a/saml/acs/'

    assert _login_base()
    reqs = _get_requests(login_redirect)
    assert reqs['main'] is not None
    assert reqs['main'].response.status_code == 403

    # pylint: disable=W0212
    res_body = reqs['main'].response._body.decode('utf-8')
    error_msg = 'You are not allowed to access this app'
    error_code = 'Error code: 1124 (USER_MISMATCH)'
    error_reason = 'Reason: User identifier mismatch'
    assert res_body.find(error_msg) != -1
    assert res_body.find(error_code) != -1
    assert res_body.find(error_reason) != -1

    DRIVER.get_log('browser')  # clean errors


def login_success():
    print('TESTING LOGIN SUCCESS')
    url = f'{BASE_URL}/a/login/'
    _open_and_wait_for_load(url)

    DRIVER.find_element(By.ID, 'id_username').send_keys('user@example.com')
    DRIVER.find_element(By.ID, 'id_username').send_keys(Keys.RETURN)

    assert _login_base()
    reqs = _get_requests(f'{BASE_URL}/ui')

    for sr in reqs['sub']:
        if sr.url == f'{BASE_URL}/a/saml/acs/':
            assert sr.response.status_code == 302

    assert reqs['main'] is not None
    assert reqs['main'].response.status_code == 200


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


def _click_on(element: str, cls: bool = False):
    if cls:
        DRIVER.execute_script(
            'arguments[0].click()',
            DRIVER.find_element(By.CLASS_NAME, element),
        )

    else:
        DRIVER.execute_script(
            'arguments[0].click()',
            DRIVER.find_element(By.ID, element),
        )

def logout():
    print('TRIGGER LOGOUT')
    url = f'{BASE_URL}/ui'
    _open_and_wait_for_load(url)
    DRIVER.refresh()
    _wait_for_load()

    url = f'{BASE_URL}/o/'
    _click_on('nav-btn-logout')

    sleep(1)
    assert _check_requests(url)
    assert _check_console_logs(url)

    login_redirect = f'{BASE_URL}/a/login/'
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
            sleep(1)  # wait for JS async fetches (in case they would fail)

            assert _check_requests(url, sub=True)
            assert _check_console_logs(url)


def test_auth_pages():
    test_get_locations({
        'a/login/': {},
        'a/login/fallback/': {},
    })


def test_main_pages():
    test_get_locations({
        'ui': {
            'tab-jobs': '#jobs',
            'tab-dashboard': '#dashboard',
        },
        'ui/system': {
            'tab-settings': '#settings',
        },
    })


def main():
    try:
        test_auth_pages()
        login_failure()

        login_success()
        test_main_pages()
        logout()

        login_fallback(user=environ['AW_ADMIN'], pwd=environ['AW_ADMIN_PWD'])
        test_main_pages()

    finally:
        DRIVER.quit()


if __name__ == '__main__':
    main()
