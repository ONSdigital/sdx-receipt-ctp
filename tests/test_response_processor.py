import logging
import os
import unittest

from app.response_processor import ResponseProcessor
from tests.test_data import valid_decrypted, invalid_decrypted

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

class TestResponseProcessorSettings(unittest.TestCase):

    @unittest.skipIf(
        "SDX_RECEIPT_CTP_SECRET" in os.environ,
        "variables match live environment"
    )
    def test_no_settings_only_env(self):
        try:
            os.environ["SDX_RECEIPT_CTP_SECRET"] = "y" * 44
            self.assertTrue(os.getenv("SDX_RECEIPT_CTP_SECRET"))
            rv = ResponseProcessor.options()
            self.assertEqual({"secret": b"y" * 44}, rv)
        finally:
            del os.environ["SDX_RECEIPT_CTP_SECRET"]

    def test_no_settings(self):
        rv = ResponseProcessor.options()
        self.assertEqual({}, rv)

class TestResponseProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = ResponseProcessor(logger)
        self.processor.skip_receipt = True

    def test_valid_case_ref(self):
        result = self.processor.process(valid_decrypted)
        self.assertTrue(result)

    def test_invalid_case_ref(self):
        result = self.processor.process(invalid_decrypted)
        self.assertFalse(result)
