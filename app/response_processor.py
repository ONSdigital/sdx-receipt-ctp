from app import settings
from app.settings import session
from json import loads
from app.helpers.exceptions import BadMessageError, RetryableError, DecryptError

from cryptography.fernet import Fernet
from requests.packages.urllib3.exceptions import MaxRetryError


class ResponseProcessor:

    def __init__(self, logger):
        self.logger = logger
        self.tx_id = ""

    def process(self, message, **kwargs):

        # Decrypt
        try:
            message = self._decrypt(token=message, secret=settings.SDX_RECEIPT_RRM_SECRET)
        except Exception as e:
            self.logger.error("Exception decrypting message", exception=e)
            raise DecryptError("Failed to decrypt")

        # Validate
        decrypted_json = loads(message)
        self._validate(decrypted_json)

        # Encode
        data = self._encode(decrypted_json)

        # Send
        self._send_receipt(decrypted_json, data)

        return

    def _validate(self, decrypted):
        if 'tx_id' not in decrypted:
            raise BadMessageError("Missing tx_id")
        self.tx_id = decrypted['tx_id']
        self.logger = self.logger.bind(tx_id=self.tx_id)

        if 'metadata' not in decrypted:
            raise BadMessageError("Missing metadata")

        if 'ru_ref' not in decrypted['metadata'] or not decrypted['metadata']['ru_ref']:
            raise BadMessageError("Missing ru_ref in metadata")
        return

    def _decrypt(self, token, secret):
        f = Fernet(secret)
        try:
            message = f.decrypt(token)
        except TypeError:
            message = f.decrypt(token.encode("utf-8"))
        return message.decode("utf-8")

    def _encode(self, decrypted):
        if 'metadata' in decrypted and 'ru_ref' in decrypted['metadata']:
            return {'caseRef': decrypted['metadata']['ru_ref']}
        raise BadMessageError('Missing metadata')

    def _send_receipt(self, decrypted, data):
        endpoint = settings.RECEIPT_HOST + "/" + settings.RECEIPT_PATH
        if endpoint == "/":
            raise BadMessageError("Unable to determine delivery endpoint from message")

        headers = None
        auth = (settings.RECEIPT_USER, settings.RECEIPT_PASS)

        res_logger = self.logger.bind(request_url=endpoint)

        try:
            res_logger.info("Calling service")
            res = session.post(endpoint, data=data, headers=headers, verify=False, auth=auth)

            res_logger = res_logger.bind(stats_code=res.status_code)

            if res.status_code == 400:
                res_logger.error("Receipt rejected by endpoint")
                raise BadMessageError("Failure to send receipt")

            elif res.status_code != 200 and res.status_code != 201:
                # Endpoint may be temporarily down
                res_logger.error("Bad response from endpoint")
                raise RetryableError("Bad response from endpoint")

            else:
                res_logger.info("Sent receipt")
                return

        except MaxRetryError:
            res_logger.error("Max retries exceeded (5) attempting to send to endpoint")
            raise RetryableError("Failure to send receipt")
