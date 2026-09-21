import unittest

from markdown import split_nodes_delimiter
from markdown import extract_markdown_images
from markdown import extract_markdown_links
from markdown import split_nodes_image
from markdown import split_nodes_link
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
	def test_splits_text_node_at_delimiter(self):
		old_nodes = [TextNode("This is *bold* text", TextType.TEXT)]

		result = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)

		self.assertEqual(
			result,
			[
				TextNode("This is ", TextType.TEXT),
				TextNode("bold", TextType.BOLD),
				TextNode(" text", TextType.TEXT),
			],
		)

	def test_splits_multiple_delimited_segments(self):
		old_nodes = [TextNode("*bold* and *also bold*", TextType.TEXT)]

		result = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)

		self.assertEqual(
			result,
			[
				TextNode("bold", TextType.BOLD),
				TextNode(" and ", TextType.TEXT),
				TextNode("also bold", TextType.BOLD),
			],
		)

	def test_splits_multiple_input_nodes(self):
		old_nodes = [
			TextNode("First *bold* item", TextType.TEXT),
			TextNode("Second plain item", TextType.TEXT),
			TextNode("Third *bold* item", TextType.TEXT),
		]

		result = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)

		self.assertEqual(
			result,
			[
				TextNode("First ", TextType.TEXT),
				TextNode("bold", TextType.BOLD),
				TextNode(" item", TextType.TEXT),
				TextNode("Second plain item", TextType.TEXT),
				TextNode("Third ", TextType.TEXT),
				TextNode("bold", TextType.BOLD),
				TextNode(" item", TextType.TEXT),
			],
		)

	def test_ignores_empty_segments(self):
		old_nodes = [TextNode("*bold*", TextType.TEXT)]

		result = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)

		self.assertEqual(result, [TextNode("bold", TextType.BOLD)])

	def test_preserves_non_text_nodes(self):
		old_node = TextNode("already bold", TextType.BOLD)

		result = split_nodes_delimiter([old_node], "*", TextType.ITALIC)

		self.assertEqual(result, [old_node])

	def test_raises_for_unmatched_delimiter(self):
		old_nodes = [TextNode("This is *not closed", TextType.TEXT)]

		with self.assertRaises(Exception):
			split_nodes_delimiter(old_nodes, "*", TextType.BOLD)


class TestExtractMarkdownImages(unittest.TestCase):
	def test_extracts_multiple_images(self):
		text = (
			"This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
			"and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
		)

		result = extract_markdown_images(text)

		self.assertEqual(
			result,
			[
				("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
				("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
			],
		)

	def test_returns_empty_list_when_no_images_exist(self):
		self.assertEqual(extract_markdown_images("plain text"), [])


class TestSplitNodesImage(unittest.TestCase):
	def test_splits_single_image_with_surrounding_text(self):
		old_nodes = [
			TextNode("Before ![alt text](image.png) after", TextType.TEXT)
		]

		result = split_nodes_image(old_nodes)

		self.assertEqual(
			result,
			[
				TextNode("Before ", TextType.TEXT),
				TextNode("alt text", TextType.IMAGE, "image.png"),
				TextNode(" after", TextType.TEXT),
			],
		)

	def test_splits_multiple_images(self):
		old_nodes = [
			TextNode(
				"First ![one](one.png), then ![two](two.jpg).",
				TextType.TEXT,
			)
		]

		result = split_nodes_image(old_nodes)

		self.assertEqual(
			result,
			[
				TextNode("First ", TextType.TEXT),
				TextNode("one", TextType.IMAGE, "one.png"),
				TextNode(", then ", TextType.TEXT),
				TextNode("two", TextType.IMAGE, "two.jpg"),
				TextNode(".", TextType.TEXT),
			],
		)

	def test_preserves_text_without_images(self):
		old_node = TextNode("plain text", TextType.TEXT)

		self.assertEqual(split_nodes_image([old_node]), [old_node])

	def test_preserves_non_text_nodes(self):
		old_node = TextNode("already bold", TextType.BOLD)

		self.assertEqual(split_nodes_image([old_node]), [old_node])

	def test_splits_images_across_multiple_input_nodes(self):
		old_nodes = [
			TextNode("First ![image](first.png)", TextType.TEXT),
			TextNode("Second plain node", TextType.TEXT),
		]

		result = split_nodes_image(old_nodes)

		self.assertEqual(
			result,
			[
				TextNode("First ", TextType.TEXT),
				TextNode("image", TextType.IMAGE, "first.png"),
				TextNode("Second plain node", TextType.TEXT),
			],
		)


class TestExtractMarkdownLinks(unittest.TestCase):
	def test_extracts_multiple_links(self):
		text = (
			"This is text with a link [to boot dev](https://www.boot.dev) "
			"and [to youtube](https://www.youtube.com/@bootdotdev)"
		)

		result = extract_markdown_links(text)

		self.assertEqual(
			result,
			[
				("to boot dev", "https://www.boot.dev"),
				("to youtube", "https://www.youtube.com/@bootdotdev"),
			],
		)

	def test_does_not_extract_images_as_links(self):
		self.assertEqual(
			extract_markdown_links("![image](https://example.com/image.png)"),
			[],
		)

	def test_returns_empty_list_when_no_links_exist(self):
		self.assertEqual(extract_markdown_links("plain text"), [])


class TestSplitNodesLink(unittest.TestCase):
	def test_splits_single_link_with_surrounding_text(self):
		old_nodes = [
			TextNode("Before [link text](https://example.com) after", TextType.TEXT)
		]

		result = split_nodes_link(old_nodes)

		self.assertEqual(
			result,
			[
				TextNode("Before ", TextType.TEXT),
				TextNode("link text", TextType.LINK, "https://example.com"),
				TextNode(" after", TextType.TEXT),
			],
		)

	def test_splits_multiple_links(self):
		old_nodes = [
			TextNode(
				"First [one](one.example), then [two](two.example).",
				TextType.TEXT,
			)
		]

		result = split_nodes_link(old_nodes)

		self.assertEqual(
			result,
			[
				TextNode("First ", TextType.TEXT),
				TextNode("one", TextType.LINK, "one.example"),
				TextNode(", then ", TextType.TEXT),
				TextNode("two", TextType.LINK, "two.example"),
				TextNode(".", TextType.TEXT),
			],
		)

	def test_does_not_split_images_as_links(self):
		old_node = TextNode("![image](image.png)", TextType.TEXT)

		self.assertEqual(split_nodes_link([old_node]), [old_node])

	def test_preserves_text_without_links(self):
		old_node = TextNode("plain text", TextType.TEXT)

		self.assertEqual(split_nodes_link([old_node]), [old_node])

	def test_preserves_non_text_nodes(self):
		old_node = TextNode("already bold", TextType.BOLD)

		self.assertEqual(split_nodes_link([old_node]), [old_node])


if __name__ == "__main__":
	unittest.main()
