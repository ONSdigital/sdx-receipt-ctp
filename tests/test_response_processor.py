import unittest
import mock
import json

from cryptography.fernet import Fernet, InvalidToken
from app.response_processor import ResponseProcessor
from app.helpers.exceptions import BadMessageError, RetryableError
from tests.test_data import test_secret, test_data
from app import settings

import logging
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))
processor = ResponseProcessor(logger)
settings.SDX_RECEIPT_RRM_SECRET = test_secret


def encrypt(plain):
    f = Fernet(test_secret)
    return f.encrypt(plain.encode("utf-8"))


class MockResponse:
    def __init__(self, status):
        self.status_code = status
        self.url = ""


class TestResponseProcessor(unittest.TestCase):

    def test_with_valid_data(self):
        with mock.patch('app.response_processor.session.post') as session_mock:
            session_mock.return_value = MockResponse(status=200)
            processor.process(encrypt(test_data['valid']))

    def test_with_invalid_data(self):
        with mock.patch('app.response_processor.session.post') as session_mock:
            session_mock.return_value = MockResponse(status=200)
            for case in ('invalid', 'missing_metadata'):
                with self.assertRaises(BadMessageError):
                    processor.process(encrypt(test_data[case]))


class TestDecrypt(unittest.TestCase):

    def test_decrypt_with_bad_token(self):
        with self.assertRaises(InvalidToken):
            processor._decrypt("xbxhsbhxbsahb", test_secret)

    def test_decrypt_with_good_token(self):
        token = encrypt(test_data['valid'])
        plain = processor._decrypt(token, test_secret)
        self.assertEqual(plain, test_data['valid'])


class TestValidate(unittest.TestCase):

    def test_valid_data(self):
        processor._validate(json.loads(test_data['valid']))

    def test_missing_metadata(self):
        with self.assertRaises(BadMessageError):
            processor._validate(json.loads(test_data['missing_metadata']))


class TestEncode(unittest.TestCase):

    def test_with_invalid_metadata(self):
        with self.assertRaises(BadMessageError):
            processor._encode({"bad": "thing"})

    def test_with_valid_data(self):
        processor._encode(json.loads(test_data['valid']))


class TestSend(unittest.TestCase):

    def setUp(self):
        self.decrypted = json.loads(test_data['valid'])
        self.xml = processor._encode(self.decrypted)

    def test_with_200_response(self):
        with mock.patch('app.response_processor.session.post') as session_mock:
            session_mock.return_value = MockResponse(status=200)
            processor._send_receipt(self.decrypted, self.xml)

    def test_with_500_response(self):
        with self.assertRaises(RetryableError):
            with mock.patch('app.response_processor.session.post') as session_mock:
                session_mock.return_value = MockResponse(status=500)
                processor._send_receipt(self.decrypted, self.xml)

    def test_with_400_response(self):
        with self.assertRaises(BadMessageError):
            with mock.patch('app.response_processor.session.post') as session_mock:
                session_mock.return_value = MockResponse(status=400)
                processor._send_receipt(self.decrypted, self.xml)

# import base64
# import logging
# import os
# import unittest
#
# from app.response_processor import ResponseProcessor
# from tests.test_data import valid_decrypted, invalid_decrypted
#
# from structlog import wrap_logger
#
# logger = wrap_logger(logging.getLogger(__name__))
#
#
# class TestResponseProcessorSettings(unittest.TestCase):
#
#     @unittest.skipIf(
#         "SDX_RECEIPT_CTP_SECRET" in os.environ,
#         "variables match live environment"
#     )
#     def test_no_settings_only_env(self):
#         try:
#             os.environ["SDX_RECEIPT_CTP_SECRET"] = "y" * 44
#             self.assertTrue(os.getenv("SDX_RECEIPT_CTP_SECRET"))
#             rv = ResponseProcessor.options()
#             self.assertEqual({"secret": b"y" * 44}, rv)
#         finally:
#             del os.environ["SDX_RECEIPT_CTP_SECRET"]
#
#     def test_no_settings(self):
#         rv = ResponseProcessor.options()
#         self.assertEqual({}, rv)
#
#
# class DecryptionTests(unittest.TestCase):
#
#     def test_encrypt_bytes_message(self):
#         secret = base64.b64encode(b"x" * 32)
#         message = "Test string".encode("utf-8")
#         rv = ResponseProcessor.encrypt(message, secret=secret)
#         self.assertIsInstance(rv, bytes)
#         self.assertIsInstance(rv.decode("ascii"), str)
#         self.assertIsInstance(base64.urlsafe_b64decode(rv.decode("ascii")), bytes)
#
#     def test_encrypt_string_message(self):
#         secret = base64.b64encode(b"x" * 32)
#         message = "Test string"
#         rv = ResponseProcessor.encrypt(message, secret=secret)
#         self.assertIsInstance(rv, bytes)
#         self.assertIsInstance(rv.decode("ascii"), str)
#         self.assertIsInstance(base64.urlsafe_b64decode(rv.decode("ascii")), bytes)
#
#     def test_roundtrip_bytes_message(self):
#         secret = base64.b64encode(b"x" * 32)
#         message = "Test string"
#         token = ResponseProcessor.encrypt(message.encode("utf-8"), secret=secret)
#         rv = ResponseProcessor.decrypt(token, secret=secret)
#         self.assertEqual(message, rv)
#
#     def test_roundtrip_string_message(self):
#         secret = base64.b64encode(b"x" * 32)
#         message = "Test string"
#         token = ResponseProcessor.encrypt(message, secret=secret)
#         rv = ResponseProcessor.decrypt(token, secret=secret)
#         self.assertEqual(message, rv)
#
#     def test_decrypt_with_string_token(self):
#         secret = base64.b64encode(b"x" * 32)
#         message = "Test string"
#         token = ResponseProcessor.encrypt(message.encode("utf-8"), secret=secret)
#         rv = ResponseProcessor.decrypt(token.decode("utf-8"), secret=secret)
#         self.assertEqual(message, rv)
#
#
# class TestResponseProcessor(unittest.TestCase):
#
#     def setUp(self):
#         self.processor = ResponseProcessor(logger)
#         self.processor.skip_receipt = True
#
#     def test_valid_case_ref(self):
#         result = self.processor.process(valid_decrypted)
#         self.assertTrue(result)
#
#     def test_invalid_case_ref(self):
#         result = self.processor.process(invalid_decrypted)
#         self.assertFalse(result)
