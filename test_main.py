import os
import tempfile
import unittest

from main import extract_title, generate_page, generate_pages_recursive


class TestExtractTitle(unittest.TestCase):
    def test_extracts_h1_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_strips_title_whitespace(self):
        self.assertEqual(extract_title("#   Hello world  "), "Hello world")

    def test_ignores_non_h1_headings(self):
        with self.assertRaises(Exception):
            extract_title("## Not an h1")

    def test_raises_when_title_is_missing(self):
        with self.assertRaises(Exception):
            extract_title("Just a paragraph")


class TestGeneratePage(unittest.TestCase):
    def test_generates_full_html_page(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown_path = os.path.join(directory, "content", "index.md")
            template_path = os.path.join(directory, "template.html")
            destination_path = os.path.join(directory, "docs", "index.html")
            os.makedirs(os.path.dirname(markdown_path))

            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write("# Hello\n\nThis is **bold**.")
            with open(template_path, "w", encoding="utf-8") as template_file:
                template_file.write(
                    "<title>{{ Title }}</title><main>{{ Content }}</main>"
                )

            generate_page(markdown_path, template_path, destination_path)

            with open(destination_path, encoding="utf-8") as destination_file:
                page = destination_file.read()

            self.assertEqual(
                page,
                "<title>Hello</title><main><div><h1>Hello</h1>"
                "<p>This is <b>bold</b>.</p></div></main>",
            )

    def test_replaces_root_relative_asset_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown_path = os.path.join(directory, "index.md")
            template_path = os.path.join(directory, "template.html")
            destination_path = os.path.join(directory, "docs", "index.html")

            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write("# Hello\n\n![Image](/images/image.png)")
            with open(template_path, "w", encoding="utf-8") as template_file:
                template_file.write('<a href="/contact">Contact</a>{{ Content }}')

            generate_page(markdown_path, template_path, destination_path, "/repo/")

            with open(destination_path, encoding="utf-8") as destination_file:
                page = destination_file.read()

            self.assertIn('href="/repo/contact"', page)
            self.assertIn('src="/repo/images/image.png"', page)


class TestGeneratePagesRecursive(unittest.TestCase):
    def test_generates_nested_markdown_pages_and_ignores_other_files(self):
        with tempfile.TemporaryDirectory() as directory:
            content_path = os.path.join(directory, "content")
            template_path = os.path.join(directory, "template.html")
            docs_path = os.path.join(directory, "docs")
            nested_content_path = os.path.join(content_path, "blog", "post")
            os.makedirs(nested_content_path)

            with open(template_path, "w", encoding="utf-8") as template_file:
                template_file.write("<title>{{ Title }}</title>{{ Content }}")
            with open(os.path.join(content_path, "index.md"), "w", encoding="utf-8") as page:
                page.write("# Home\n\nWelcome home.")
            with open(os.path.join(nested_content_path, "index.md"), "w", encoding="utf-8") as page:
                page.write("# Post\n\nA nested post.")
            with open(os.path.join(content_path, "draft.txt"), "w", encoding="utf-8") as ignored:
                ignored.write("ignore this")

            generate_pages_recursive(content_path, template_path, docs_path)

            with open(os.path.join(docs_path, "index.html"), encoding="utf-8") as page:
                self.assertIn("<title>Home</title>", page.read())
            with open(
                os.path.join(docs_path, "blog", "post", "index.html"),
                encoding="utf-8",
            ) as page:
                self.assertIn("<title>Post</title>", page.read())
            self.assertFalse(os.path.exists(os.path.join(docs_path, "draft.txt")))

    def test_passes_basepath_to_nested_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            content_path = os.path.join(directory, "content")
            template_path = os.path.join(directory, "template.html")
            docs_path = os.path.join(directory, "docs")
            os.makedirs(content_path)

            with open(template_path, "w", encoding="utf-8") as template_file:
                template_file.write("{{ Content }}")
            with open(os.path.join(content_path, "index.md"), "w", encoding="utf-8") as page:
                page.write("# Home\n\n![Image](/images/image.png)")

            generate_pages_recursive(content_path, template_path, docs_path, "/repo/")

            with open(os.path.join(docs_path, "index.html"), encoding="utf-8") as page:
                self.assertIn('src="/repo/images/image.png"', page.read())


if __name__ == "__main__":
    unittest.main()
