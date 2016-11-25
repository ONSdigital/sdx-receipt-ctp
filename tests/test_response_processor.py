import logging
import unittest
from tests.test_data import valid_decrypted, invalid_decrypted
from structlog import wrap_logger
from app.response_processor import ResponseProcessor

logger = wrap_logger(logging.getLogger(__name__))


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
