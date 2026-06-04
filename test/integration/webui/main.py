from os import environ
from time import sleep
from pathlib import Path

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
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
DRIVER.set_window_size(1920, 1080)

DEBUG = 'AW_DEBUG' in environ
SCREENSHOT_DIR = Path('/tmp/aw-test-webui')
SCREENSHOT_DIR.mkdir(exist_ok=True)
QUERY_SELECTOR = 'QS|'


def _get_requests(url: str) -> dict:
    reqs = {'main': None, 'sub': []}

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


def login(user: str, pwd: str):
    print('TESTING LOGIN')
    url = f'{BASE_URL}/a/login/'
    _open_and_wait_for_load(url)

    DRIVER.find_element(By.ID, 'id_username').send_keys(user)
    DRIVER.find_element(By.ID, 'id_password').send_keys(pwd)
    DRIVER.find_element(By.ID, 'id_password').send_keys(Keys.RETURN)

    assert _check_requests(url)
    assert _check_console_logs(url)

    login_redirect = f'{BASE_URL}/ui'
    login_redirect2 = f'{BASE_URL}/ui#dashboard'
    sleep(1)  # we wait 500ms until we set the URL-hash
    assert DRIVER.current_url in [login_redirect, login_redirect2]


def test_get_locations(to_check: dict):
    for location, tab_fragment in to_check.items():
        print(f'TESTING GET /{location}')
        url = f'{BASE_URL}/{location}'
        _open_and_wait_for_load(url)

        assert _check_requests(url)
        assert _check_console_logs(url)

        for tab_class, fragment in tab_fragment.items():
            print(f'TESTING GET /{location}{fragment}')
            tab_class, kind = _check_kind(tab_class)
            _click_on(tab_class, kind=kind)
            _wait_for_load()
            sleep(2)  # wait for JS async fetches (in case they would fail)

            assert _check_requests(url, sub=True)
            assert _check_console_logs(url)


def test_main_pages():
    test_get_locations({
        'ui': {
            '.tab-jobs': '#jobs',
            '.tab-logs': '#logs',
            '.tab-repositories': '#repositories',
            '.tab-credentials': '#credentials',
            '.tab-alerts': '#alerts',
            '.tab-dashboard': '#dashboard',
        },
        'ui/system': {
            '.tab-admin': '#admin',
            '.tab-perm': '#permission',
            '.tab-api-keys': '#api_keys',
            '.tab-api-docs': '#api_docs',
            '.tab-settings': '#settings',
            '.tab-env': '#env',
            '.tab-ssh-hostkey': '#hostkey',
        },
    })


def test_existence():
    cnf = {
        'ui': [
            'nav-btn-home',
            'nav-btn-system',
            'nav-btn-lang',
            'nav-btn-darkmode',
            'nav-btn-docs',
            'nav-btn-repo',
            'nav-btn-bugs',
            'nav-btn-user-settings',
            'nav-btn-logout',
        ],
    }
    for location, elements in cnf.items():
        url = f'{BASE_URL}/{location}'
        _open_and_wait_for_load(url)

        for elementID in elements:
            print(f'CHECK ELEMENT /{location} {elementID}')
            if not DRIVER.find_element(By.ID, elementID):
                print(f"ERROR: Element '{elementID}' not found @ '{url}'")


def _click_on(element: str, kind: str = 'id'):
    if kind == 'id':
        DRIVER.execute_script(
            'arguments[0].click()',
            DRIVER.find_element(By.ID, element),
        )

    if kind == 'cls':
        DRIVER.execute_script(
            'arguments[0].click()',
            DRIVER.find_element(By.CLASS_NAME, element),
        )

    if kind == 'qs':
        nr = ''
        if len(element) > 4 and element.find('[') != -1 and element[-1] == ']':
            element, nr = element.split('[', 1)
            nr = f'[{nr}'

        DRIVER.execute_script(
            f"document.querySelectorAll('{element}'){nr}.click()",
        )


def _write_into_field(element: str, text: str, kind: str = 'id', cls_nr: int = 0):
    if kind == 'id':
        DRIVER.execute_script(f"document.getElementById('{element}').focus()")

    if kind == 'cls':
        DRIVER.execute_script(f"document.getElementsByClassName('{element}')[{cls_nr}].focus()")

    DRIVER.execute_script(f"document.execCommand('insertText', false, '{text}');")


def _check_kind(element: str) -> (str, str):
    if element.startswith(QUERY_SELECTOR):
        return element[3:], 'qs'

    if element.startswith('.'):
        return element[1:], 'cls'

    return element[1:], 'id'


def test_js_actions():
    start_ids = {
        'creds_user': 1,
    }


    cnf = {
        'ui': {
            '.tab-jobs': [
                ['#nav-btn-lang', '#nav-btn-lang-de'],
                ['#nav-btn-lang', '#nav-btn-lang-en'],
                [
                    '#jobs-btn-add', '.job-form-main', '.job-form-exec', '.job-form-creds', '.job-form-schedule',
                    '.job-form-extra-vars', '.job-form-misc', '.job-form-prompts',
                    '#job-btn-discard'
                ],
                # todo: test job-execution
                # todo: test tmp-credentials
                # #jobs-btn-exec-{id}, #jobs-btn-stop-{id}, #jobs-btn-logs-{id},
                # #jobs-btn-edit-{id}, #jobs-btn-clone-{id}, #jobs-btn-delete-{id}
                # #jobs-btn-exec-start, #jobs-btn-exec-close
                # todo: test open logs-view (success, failure & exception handling) - check for valid content
            ],
            '.tab-repositories': [
                ['.repos-kind-static'],
                ['.repos-kind-git'],
                ['#repos-btn-add-dd', '#repos-btn-add-static', '#repo-btn-discard'],
                [
                    '#repos-btn-add-dd', '#repos-btn-add-git', '.repo-form-git-opts', '.repo-form-git-hooks',
                    '#repo-btn-discard',
                ],
            ],
            '.tab-credentials': [
                ['.creds-kind-user'],
                ['.creds-kind-shared'],
                [
                    '#creds-btn-add-dd', '#creds-btn-add-user', '.creds-form-accounts', '.creds-form-vault',
                    '#creds-btn-discard'
                ],
                [
                    '#creds-btn-add-dd', '#creds-btn-add-shared', '.creds-form-accounts', '.creds-form-vault',
                    '#creds-btn-discard'
                ],
                [
                    '#creds-btn-add-dd', '#creds-btn-add-user', '#creds_name=test',
                    '.creds-form-accounts', '#creds_conn_user=someGuy',
                    '.creds-form-vault', '#creds_vault_pass=myTopSecret',
                    '#creds-btn-save',
                ],
                [
                    # clone user-creds
                    f'{QUERY_SELECTOR}.aw-accordion[0]', f"#creds-btn-clone-user-{start_ids['creds_user']}",
                    '#creds-btn-save',
                ],
                [
                    # delete user-creds
                    f'{QUERY_SELECTOR}.aw-accordion[0]', f"#creds-btn-delete-user-{start_ids['creds_user'] + 1}",
                    '#confirm-prompt-btn-confirm',
                ],
                [
                    # ansible-vault-encrypt text
                    f'{QUERY_SELECTOR}.aw-accordion[0]', f"#creds-btn-vaultencrypt-user-{start_ids['creds_user']}",
                    '#creds_vaultencrypt_plaintext=myNewSecret', '#creds-btn-vaultencrypt-submit',
                    '#creds-btn-vaultencrypt-close',
                ],
            ],
            '.tab-alerts': [
                ['.alerts-kind-global'],
                ['.alerts-kind-group'],
                ['.alerts-kind-user'],
                ['.alerts-kind-plugin'],
                ['#alerts-btn-add-dd', '#alerts-btn-add-global', '#alert-btn-discard'],
                ['#alerts-btn-add-dd', '#alerts-btn-add-group', '#alert-btn-discard'],
                ['#alerts-btn-add-dd', '#alerts-btn-add-user', '#alert-btn-discard'],
                ['#alerts-btn-add-dd', '#alerts-btn-add-plugin', '#plugin-btn-discard'],
            ],
        },
        # .logs-job-{job.id}, #logs-job-{job.id}-show
        'ui/system': {
            '.tab-api-keys': [
                ['#apikeys-btn-add', '#apikeys-btn-add-submit', '#apikeys-btn-add-close'],
            ],
            '.tab-settings': [
                ['.settings-exec', '.settings-paths', '.settings-mailing', '.settings-internal', '#settings-btn-save'],
            ],
            '.tab-env': [
                ['.env-main', '.env-anscnf', '.env-anscol', '.env-pymod'],
                # '#env-btn-copy'; todo fix: Uncaught DOMException: Failed to execute 'writeText' on 'Clipboard': Write permission denied."
            ],
            '.tab-perm': [
                # todo: create permission
                ['#perms-btn-add', '#perm-btn-discard'],
            ],
            '.tab-ssh-hostkey': [
                [
                    '#ssh-hostkey-btn-scan',
                    '#ssh_hostkey_target=localhost', '#ssh_hostkey_port=22', '#ssh_hostkey_cmt=test',
                    '#ssh-hostkey-btn-scan-submit',
                ],
            ],
        },
    }

    for location, tab_elements in cnf.items():
        url = f'{BASE_URL}/{location}'
        _open_and_wait_for_load(url)

        for tab_class, element_chains in tab_elements.items():
            tab_class, kind = _check_kind(tab_class)
            _click_on(tab_class, kind=kind)
            _wait_for_load()
            sleep(1)

            for i, element_chain in enumerate(element_chains):
                for i2, element in enumerate(element_chain):
                    print(f'TRIGGER JS /{location} {tab_class} CHAIN-{i} {i2} {element}')
                    element, kind = _check_kind(element)

                    field_input = None
                    if element.find('=') != -1:
                        element, field_input = element.split('=', 1)

                    if DEBUG:
                        DRIVER.save_screenshot(f'{SCREENSHOT_DIR}{location}-{tab_class}-{i}-{i2}-{element}-1.png')

                    if field_input is not None:
                        _write_into_field(element=element, text=field_input, kind=kind)

                    else:
                        _click_on(element, kind=kind)

                    if DEBUG:
                        DRIVER.save_screenshot(f'{SCREENSHOT_DIR}{location}-{tab_class}-{i}-{i2}-{element}-2-after.png')

                    sleep(1)
                    assert _check_requests(url, sub=True)
                    assert _check_console_logs(url)

                DRIVER.refresh()  # exit from open JS elements


def logout():
    print('TRIGGER LOGOUT')
    url = f'{BASE_URL}/ui'
    _open_and_wait_for_load(url)
    DRIVER.refresh()
    _wait_for_load()

    url = f'{BASE_URL}/o/'
    try:
        sleep(3)
        _click_on('nav-btn-logout')

    except NoSuchElementException:
        print('WARNING: Logout-button was not found')  # common false-positive; todo: fix
        return

    sleep(1)
    assert _check_requests(url)
    assert _check_console_logs(url)

    login_redirect = f'{BASE_URL}/a/login/'
    assert DRIVER.current_url == login_redirect


def main():
    try:
        try:
            login(user=environ['AW_ADMIN'], pwd=environ['AW_ADMIN_PWD'])
            test_main_pages()
            test_existence()
            test_js_actions()
            logout()

        except Exception:
            DRIVER.save_screenshot(SCREENSHOT_DIR / 'error.png')
            raise

    finally:
        DRIVER.quit()


if __name__ == '__main__':
    main()
