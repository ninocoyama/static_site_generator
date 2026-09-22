import os
import shutil
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from markdown import markdown_to_html_node


def copy_files(source, destination):
    if not os.path.exists(destination):
        os.mkdir(destination)

    for filename in os.listdir(source):
        source_path = os.path.join(source, filename)
        destination_path = os.path.join(destination, filename)

        if os.path.isfile(source_path):
            print(f"Copying {source_path} to {destination_path}")
            shutil.copy(source_path, destination_path)
        else:
            copy_files(source_path, destination_path)


def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()

    raise Exception("Markdown document has no h1 title")


def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from `{from_path}` to `{dest_path}` using `{template_path}`")

    with open(from_path, encoding="utf-8") as markdown_file:
        markdown = markdown_file.read()

    with open(template_path, encoding="utf-8") as template_file:
        template = template_file.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)
    page = page.replace('href="/', f'href="{basepath}')
    page = page.replace('src="/', f'src="{basepath}')

    destination_directory = os.path.dirname(dest_path)
    if destination_directory:
        os.makedirs(destination_directory, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as destination_file:
        destination_file.write(page)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    for filename in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, filename)

        if os.path.isfile(source_path):
            if not filename.endswith(".md"):
                continue

            destination_filename = os.path.splitext(filename)[0] + ".html"
            destination_path = os.path.join(dest_dir_path, destination_filename)
            generate_page(source_path, template_path, destination_path, basepath)
        else:
            destination_path = os.path.join(dest_dir_path, filename)
            os.makedirs(destination_path, exist_ok=True)
            generate_pages_recursive(source_path, template_path, destination_path, basepath)


def main():
    static_path = os.path.join(PROJECT_ROOT, "static")
    docs_path = os.path.join(PROJECT_ROOT, "docs")
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    if os.path.exists(docs_path):
        shutil.rmtree(docs_path)

    copy_files(static_path, docs_path)
    generate_pages_recursive(
        os.path.join(PROJECT_ROOT, "content"),
        os.path.join(PROJECT_ROOT, "template.html"),
        docs_path,
        basepath,
    )


if __name__ == "__main__":
    main()