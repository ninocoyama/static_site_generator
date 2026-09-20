import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

props_test = {
    "href": "https://www.google.com",
    "target": "_blank",
}

class TestHTMLNode(unittest.TestCase):

    #HTMLNode tests
    def test_props_to_html_with_no_props(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_with_one_prop(self):
        node = HTMLNode(props={"class": "container"})
        self.assertEqual(node.props_to_html(), ' class="container"')

    def test_props_to_html_with_multiple_props(self):
        node = HTMLNode(props=props_test)
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    #LeafNode tests
    def test_leaf_node_requires_tag_and_value(self):
        with self.assertRaises(TypeError):
            LeafNode("p")
        with self.assertRaises(TypeError):
            LeafNode()

    def test_leaf_node_to_html_with_tag(self):
        node = LeafNode("p", "Hello")
        self.assertEqual(node.to_html(), "<p>Hello</p>")

    def test_leaf_node_to_html_without_tag(self):
        node = LeafNode(None, "Hello")
        self.assertEqual(node.to_html(), "Hello")

    def test_leaf_node_to_html_with_props(self):
        node = LeafNode("a", "Click", props=props_test)
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com" target="_blank">Click</a>',
        )

    def test_leaf_node_to_html_requires_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_node_repr(self):
        node = LeafNode("p", "Hello", props={"class": "intro"})
        self.assertEqual(
            repr(node),
            "HTMLNode(p, Hello, {'class': 'intro'})",
        )

    #ParentNode tests
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")


    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        children = [LeafNode("p", "first"), LeafNode("p", "second")]
        parent_node = ParentNode("main", children)
        self.assertEqual(
            parent_node.to_html(),
            "<main><p>first</p><p>second</p></main>",
        )

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "content")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="container"><span>content</span></div>',
        )

    def test_to_html_requires_tag(self):
        parent_node = ParentNode(None, [LeafNode("span", "content")])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_requires_children(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

    


if __name__ == "__main__":
    unittest.main()