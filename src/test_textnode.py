import unittest

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_creation(self):
        node = TextNode("Example text", TextType.TEXT)
        self.assertEqual(node.text, "Example text")
        self.assertEqual(node.text_type, TextType.TEXT)
        self.assertIsNone(node.url)

    def test_link_node(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        self.assertEqual(node.text, "Click here")
        self.assertEqual(node.text_type, TextType.LINK)
        self.assertEqual(node.url, "https://example.com")

    def test_eq(self):
        node1 = TextNode("Text", TextType.BOLD)
        node2 = TextNode("Text", TextType.BOLD)
        node3 = TextNode("Different", TextType.BOLD)
        self.assertEqual(node1, node2)
        self.assertNotEqual(node1, node3)

    def test_eq_url(self):
        node = TextNode("This is a text node", TextType.TEXT, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.TEXT, "https://www.boot.dev")
        self.assertEqual(node, node2)

    def test_url_none_vs_value(self):
        node1 = TextNode("Text", TextType.LINK, None)
        node2 = TextNode("Text", TextType.LINK, "https://example.com")
        self.assertNotEqual(node1, node2)

    def test_repr(self):
        node = TextNode("Sample", TextType.ITALIC, "https://sample.com")
        self.assertEqual(repr(node), "TextNode(Sample, italic, https://sample.com)")

    def test_diff_txt_type(self):
        node1 = TextNode("Text", TextType.TEXT)
        node2 = TextNode("Text", TextType.BOLD)
        self.assertNotEqual(node1, node2)

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_image(self):
        node = TextNode("This is an image", TextType.IMAGE, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://www.boot.dev", "alt": "This is an image"},
        )

    def test_bold(self):
        node = TextNode("This is bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold")


if __name__ == "__main__":
    unittest.main()