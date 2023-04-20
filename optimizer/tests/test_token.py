"""Unit tests for token.py."""
import unittest

from optimizer.gpt.token import num_tokens_from_string, num_tokens_from_messages
from optimizer.gpt.api import MODEL


class TestNumTokensFromString(unittest.TestCase):
    """Unit tests for num_tokens_from_string."""

    def test_num_tokens_from_string(self):
        """Unit test for num_tokens_from_string."""
        string = "tiktoken is great!"
        encoding_name = MODEL
        num_tokens = num_tokens_from_string(string, encoding_name)
        self.assertEqual(num_tokens, 6)

    def test_num_tokens_from_messages(self):
        """Unit test for num_tokens_from_messages."""
        messages = [
            {"role": "user", "content": "Tell me who you are."},
            {"role": "assistant", "name": "GPT", "content": "I am GPT."},
        ]
        encoding_name = MODEL
        num_tokens = num_tokens_from_messages(messages, encoding_name)
        self.assertEqual(num_tokens, 25)
