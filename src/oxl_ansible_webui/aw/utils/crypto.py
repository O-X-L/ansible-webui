from hashlib import sha256
from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from aw.config.main import config
from aw.utils.util import is_null
from aw.utils.debug import log_warn, log

__KEY = sha256(config['secret'].encode('utf-8')).digest()


def _get_secret(secret: (str, None)) -> bytes:
    if is_null(secret):
        return __KEY

    return sha256(secret.encode('utf-8')).digest()


def encrypt(plaintext: str, secret: str = None) -> str:
    if is_null(plaintext):
        return ''

    try:
        return _encrypt(
            plaintext=plaintext.encode('utf-8'),
            secret=_get_secret(secret),
        ).decode('utf-8')

    except ValueError as err:
        log_warn("Unable to encrypt data!")
        log(msg=f"Got error encrypting plaintext: '{err}'", level=6)
        return ''


def _encrypt(plaintext: bytes, secret: bytes) -> bytes:
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    ciphertext = iv + cipher.encrypt(
        plaintext=pad(
            data_to_pad=plaintext,
            block_size=AES.block_size,
            style='pkcs7',
        ),
    )
    return b64encode(ciphertext)


def decrypt(ciphertext: str, secret: str = None) -> str:
    if is_null(ciphertext):
        return ''

    try:

        return _decrypt(
            ciphertext=ciphertext.encode('utf-8'),
            secret=_get_secret(secret),
        ).decode('utf-8')

    except ValueError as err:
        if secret is None:
            log_warn("Unable to decrypt secret! Maybe the key 'AW_SECRET' changed?")

        else:
            log_warn("Unable to decrypt secret! Maybe the provided secret does not match.")

        log(msg=f"Got error decrypting ciphertext: '{err}'", level=6)
        return ''


def _decrypt(ciphertext: bytes, secret: bytes) -> bytes:
    ciphertext = b64decode(ciphertext)
    cipher = AES.new(secret, AES.MODE_CBC, ciphertext[:AES.block_size])
    return unpad(
        padded_data=cipher.decrypt(ciphertext[AES.block_size:]),
        block_size=AES.block_size,
        style='pkcs7',
    )
