import unittest

from optimizer.utils.extract import extract_by_quotation_mark, extract_code, extract_html_list


class TestExtractByQuotationMark(unittest.TestCase):
    def test_single_quote(self):
        result = extract_by_quotation_mark(
            "The 'quick brown' fox jumps over the lazy dog.")
        self.assertEqual(result, 'quick brown')

    def test_double_quote(self):
        result = extract_by_quotation_mark(
            'The "quick brown" fox jumps over the lazy dog.')
        self.assertEqual(result, 'quick brown')

    def test_no_quote(self):
        result = extract_by_quotation_mark(
            'The quick brown fox jumps over the lazy dog.')
        self.assertIsNone(result)

    def test_empty_string(self):
        result = extract_by_quotation_mark('')
        self.assertIsNone(result)


class TestExtractCode(unittest.TestCase):
    def test_extract_python_code(self):
        input_str = r"Here is some text\n```python\nprint('hello, world!')\n```"
        expected_output = r"\nprint('hello, world!')\n"
        self.assertEqual(extract_code(input_str), expected_output)

    def test_extract_html_code(self):
        input_str = r"Here is some text\n```html\n<div>Hello, world!</div>\n```"
        expected_output = r"\n<div>Hello, world!</div>\n"
        self.assertEqual(extract_code(input_str), expected_output)

    def test_extract_inline_code(self):
        input_str = r"Here is some text with ```inline code```."
        expected_output = "inline code"
        self.assertEqual(extract_code(input_str), expected_output)

    def test_extract_none(self):
        input_str = "Here is some text."
        self.assertIsNone(extract_code(input_str))


class TestExtractHTMLList(unittest.TestCase):
    def test_extract_html_list_with_matching_li_tags(self):
        content = r"<ul><li>item1</li><li>item2</li><li>item3</li></ul>"
        expected_output = ['item1', 'item2', 'item3']
        self.assertEqual(extract_html_list(content), expected_output)

    def test_extract_html_list_with_matching_li_tags_and_newlines(self):
        content = """<ul>
                        <li>item1</li>
                        <li>item2</li>
                        <li>item3</li>
                     </ul>"""
        expected_output = ['item1', 'item2', 'item3']
        self.assertEqual(extract_html_list(content), expected_output)

    def test_extract_html_list_without_matching_li_tags(self):
        content = r"<ul><div>item1</div><div>item2</div><div>item3</div></ul>"
        expected_output = None
        self.assertEqual(extract_html_list(content), expected_output)

    def test_extract_html_list_with_multiple_patterns(self):
        content = r"""<ul>
                        <li>item1</li>
                        <li><strong>item2</strong></li>
                        <li>item3</li>
                     </ul>"""
        expected_output = ['item1', '<strong>item2</strong>', 'item3']
        self.assertEqual(extract_html_list(content), expected_output)

    def test_extract_html_list_with_empty_content(self):
        content = ""
        expected_output = None
        self.assertEqual(extract_html_list(content), expected_output)


if __name__ == '__main__':
    unittest.main()
