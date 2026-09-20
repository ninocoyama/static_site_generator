import unittest
from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("Test this", TextType.ITALIC)
        node1 = TextNode("Test this", TextType.LINK)
        self.assertNotEqual(node, node1)

    def test_url(self):
        node = TextNode("Test this", TextType.ITALIC, None)
        node2 = TextNode("Test this", TextType.ITALIC, None)
        self.assertEqual(node, node2)

    #text type testing
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a bold text node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.to_html(), "<b>This is a bold text node</b>")

    def test_italic(self):
        node = TextNode("This is an italic text node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.to_html(), "<i>This is an italic text node</i>")

    def test_code_node(self):
        node = TextNode("This is a code text node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.to_html(), "<code>This is a code text node</code>")

    def test_link_node(self):
        node = TextNode(
            "This is a link node",
            TextType.LINK,
            "https://example.com",
        )
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(
            html_node.to_html(),
            '<a href="https://example.com">This is a link node</a>',
        )

    def test_image_node(self):
        node = TextNode(
            "An example image",
            TextType.IMAGE,
            "https://example.com/image.png",
        )
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(
            html_node.to_html(),
            '<img src="https://example.com/image.png" alt="An example image"></img>',
        )

    def test_invalid_texttype(self):
        node = TextNode("This is an invalid text node", "cat")
        with self.assertRaises(Exception):
            text_node_to_html_node(node)


if __name__ == "__main__":
    unittest.main()