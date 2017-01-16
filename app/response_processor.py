from app import settings
from app.settings import session
from json import loads
import os

from cryptography.fernet import Fernet
from requests.packages.urllib3.exceptions import MaxRetryError


class ResponseProcessor:

    @staticmethod
    def options():
        rv = {}
        try:
            rv["secret"] = os.getenv("SDX_RECEIPT_CTP_SECRET").encode("ascii")
        except Exception:
            # No secret in env
            pass
        return rv

    @staticmethod
    def encrypt(message, secret):
        """
        Message may be a string or bytes.
        Secret key must be 32 url-safe base64-encoded bytes.

        """
        try:
            f = Fernet(secret)
        except ValueError:
            return None
        try:
            token = f.encrypt(message)
        except TypeError:
            token = f.encrypt(message.encode("utf-8"))
        return token

    @staticmethod
    def decrypt(token, secret):
        """
        Secret key must be 32 url-safe base64-encoded bytes or string

        Returned value is a string.
        """
        try:
            f = Fernet(secret)
        except ValueError:
            return None
        try:
            message = f.decrypt(token)
        except TypeError:
            message = f.decrypt(token.encode("utf-8"))
        return message.decode("utf-8")

    def __init__(self, logger):
        self.logger = logger
        self.tx_id = ""
        if settings.RECEIPT_HOST == "skip":
            self.skip_receipt = True
        else:
            self.skip_receipt = False

    def process(self, message, **kwargs):
        try:
            secret = kwargs.pop("secret")
            message = ResponseProcessor.decrypt(message, secret=secret)
        except KeyError:
            # No secret defined; message is plaintext
            pass

        decrypted_json = loads(message)

        if 'tx_id' in decrypted_json:
            self.tx_id = decrypted_json['tx_id']
            self.logger = self.logger.bind(tx_id=self.tx_id)

        if 'ru_ref' in decrypted_json['metadata'] and decrypted_json['metadata']['ru_ref']:
            receipt_ok = self.send_receipt(decrypted_json)
        else:
            self.logger.error("Invalid or missing case_ref")
            return False

        if not receipt_ok:
            return False
        else:
            return True

    def send_receipt(self, decrypted_json):
        if self.skip_receipt:
            self.logger.debug("Skipping sending receipt to CTP")
            return True
        else:
            self.logger.debug("Sending receipt to CTP")

        host = settings.RECEIPT_HOST
        path = settings.RECEIPT_PATH

        endpoint = host + "/" + path

        receipt = {'caseRef': decrypted_json['metadata']['ru_ref']}

        response = self.remote_call(
            endpoint,
            json=receipt,
            verify=False,
            auth=(settings.RECEIPT_USER, settings.RECEIPT_PASS))
        return self.response_ok(response)

    def remote_call(self, request_url, json=None, headers=None, verify=True, auth=None):
        try:
            self.logger.info("Calling service", request_url=request_url)
            r = None

            if json:
                r = session.post(request_url, json=json, headers=headers, verify=verify, auth=auth)
            else:
                r = session.get(request_url, headers=headers, verify=verify, auth=auth)

            return r

        except MaxRetryError:
            self.logger.error("Max retries exceeded (5)", request_url=request_url)

    def response_ok(self, res):
        if res.status_code == 200 or res.status_code == 201:
            self.logger.info("Returned from service", request_url=res.url, status_code=res.status_code)
            return True

        else:
            self.logger.error("Returned from service", request_url=res.url, status_code=res.status_code)
            return False
