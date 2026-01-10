import unittest
from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_to_html_props(self):
        node = HTMLNode(
            tag="div",
            value="Hello, World!",
            children=None,
            props={"class": "greeting", "href": "https://example.com"}
        )
    def test_values(self):
        node = HTMLNode(
            tag="span",
            value="Sample Text",
            children=None,
            props={"id": "sample", "style": "color:red;"}
        )
        self.assertEqual(node.tag, "span")
        self.assertEqual(node.value, "Sample Text")
        self.assertEqual(node.children, None)
        self.assertEqual(node.props, {"id": "sample", "style": "color:red;"})

    def test_repr(self):
        node = HTMLNode(
            tag="p",
            value="Paragraph",
            children=None,
            props={"align": "center"}
        )
        expected_repr = "HTMLNode(p, Paragraph, None, {'align': 'center'})"
        self.assertEqual(repr(node), expected_repr)
        