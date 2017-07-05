from json import loads
import xml.etree.ElementTree as etree

from cryptography.fernet import Fernet
from requests.packages.urllib3.exceptions import MaxRetryError

from app import settings
from app.settings import session
from app.helpers.exceptions import BadMessageError, RetryableError, DecryptError


class ResponseProcessor:

    def __init__(self, logger):
        self.logger = logger
        self.tx_id = ""

    def process(self, message, **kwargs):

        # Decrypt
        try:
            message = self._decrypt(token=message, secret=settings.SDX_RECEIPT_CTP_SECRET)
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

        headers = {'content-type': 'application/json'}
        auth = (settings.RECEIPT_USER, settings.RECEIPT_PASS)

        res_logger = self.logger.bind(request_url=endpoint)

        try:
            res_logger.info("Calling service", service="CTP_RECEIPT_HOST")
            res = session.post(endpoint, json=data, headers=headers, verify=False, auth=auth)

            res_logger = res_logger.bind(status=res.status_code)

            if res.status_code == 400:
                res_logger.error("Receipt rejected by endpoint")
                raise BadMessageError("Receipt rejected by endpoint")

            elif res.status_code == 404:
                namespaces = {'error': 'http://ns.ons.gov.uk/namespaces/resources/error'}
                tree = etree.fromstring(res.content)
                element = tree.find('error:message', namespaces).text
                elements = element.split('-')

                if elements[0] == '1009':
                    stat_unit_id = elements[-1].split('statistical_unit_id: ')[-1].split()[0]
                    collection_exercise_sid = elements[-1].split('collection_exercise_sid: ')[-1].split()[0]

                    res_logger.error("Receipt rejected by endpoint",
                                     msg="No records were found on the man_ce_sample_map table",
                                     error=1009,
                                     stat_unit_id=stat_unit_id,
                                     collection_exercise_sid=collection_exercise_sid)

                    raise BadMessageError("Receipt rejected by endpoint")

                else:
                    res_logger.error("Bad response from endpoint")
                    raise RetryableError("Bad response from endpoint")

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
