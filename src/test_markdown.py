import unittest

from markdown import split_nodes_delimiter
from markdown import extract_markdown_images
from markdown import extract_markdown_links
from markdown import split_nodes_image
from markdown import split_nodes_link
from markdown import markdown_to_blocks
from markdown import text_to_textnodes
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


class TestTextToTextNodes(unittest.TestCase):
	def test_converts_markdown_to_text_nodes(self):
		text = (
			"This is **bold**, _italic_, and `code` with "
			"![an image](image.png) and [a link](https://example.com)."
		)

		result = text_to_textnodes(text)

		self.assertEqual(
			result,
			[
				TextNode("This is ", TextType.TEXT),
				TextNode("bold", TextType.BOLD),
				TextNode(", ", TextType.TEXT),
				TextNode("italic", TextType.ITALIC),
				TextNode(", and ", TextType.TEXT),
				TextNode("code", TextType.CODE),
				TextNode(" with ", TextType.TEXT),
				TextNode("an image", TextType.IMAGE, "image.png"),
				TextNode(" and ", TextType.TEXT),
				TextNode("a link", TextType.LINK, "https://example.com"),
				TextNode(".", TextType.TEXT),
			],
		)

	def test_empty_text_returns_no_nodes(self):
		self.assertEqual(text_to_textnodes(""), [])

	def test_plain_text_remains_one_text_node(self):
		self.assertEqual(
			text_to_textnodes("plain text"),
			[TextNode("plain text", TextType.TEXT)],
		)

	def test_handles_adjacent_formatted_segments(self):
		self.assertEqual(
			text_to_textnodes("**bold****also bold**"),
			[
				TextNode("bold", TextType.BOLD),
				TextNode("also bold", TextType.BOLD),
			],
		)

	def test_handles_image_or_link_only_input(self):
		self.assertEqual(
			text_to_textnodes("![image](image.png)"),
			[TextNode("image", TextType.IMAGE, "image.png")],
		)
		self.assertEqual(
			text_to_textnodes("[link](https://example.com)"),
			[TextNode("link", TextType.LINK, "https://example.com")],
		)


class TestMarkdownToBlocks(unittest.TestCase):
	def test_splits_markdown_into_blocks(self):
		markdown = "# Heading\n\nThis is a paragraph.\n\nAnother paragraph."

		self.assertEqual(
			markdown_to_blocks(markdown),
			["# Heading", "This is a paragraph.", "Another paragraph."],
		)

	def test_strips_whitespace_from_each_block(self):
		markdown = "  # Heading  \n\n  Paragraph with spaces.  "

		self.assertEqual(
			markdown_to_blocks(markdown),
			["# Heading", "Paragraph with spaces."],
		)

	def test_ignores_empty_blocks(self):
		markdown = "First\n\n\n\nSecond\n\n   \n\nThird"

		self.assertEqual(markdown_to_blocks(markdown), ["First", "Second", "Third"])

	def test_ignores_empty_block_from_three_consecutive_newlines(self):
		markdown = "First\n\n\nSecond"

		self.assertEqual(markdown_to_blocks(markdown), ["First", "Second"])

	def test_preserves_single_newlines_inside_a_block(self):
		markdown = "- first item\n- second item\n\nParagraph"

		self.assertEqual(
			markdown_to_blocks(markdown),
			["- first item\n- second item", "Paragraph"],
		)


if __name__ == "__main__":
	unittest.main()
