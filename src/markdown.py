import re
from textnode import TextNode, TextType
from enum import Enum
from htmlnode import HTMLNode, ParentNode, LeafNode
from textnode import text_node_to_html_node

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []


    for old_node in old_nodes:
        if old_node.text.count(delimiter) % 2 != 0:
            raise Exception("Invalid Markdown syntax")
        
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        parts = old_node.text.split(delimiter)
        for i, part in enumerate(parts):
            if part == "":
                continue

            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes

def extract_markdown_images(text: str) -> tuple:
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text: str) -> tuple:
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        remaining_text = old_node.text
        extracted_images = extract_markdown_images(old_node.text)
        if extracted_images == []:
            new_nodes.append(old_node)
            continue

        for i in range(0, len(extracted_images)):
            parts = remaining_text.split(f"![{extracted_images[i][0]}]({extracted_images[i][1]})", 1)
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], TextType.TEXT))

            new_nodes.append(TextNode(extracted_images[i][0], TextType.IMAGE, extracted_images[i][1]))

            remaining_text = parts[1]

        if remaining_text != "":
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        remaining_text = old_node.text
        extracted_links = extract_markdown_links(old_node.text)
        if extracted_links == []:
            new_nodes.append(old_node)
            continue

        for link_text, url in extracted_links:
            parts = remaining_text.split(f"[{link_text}]({url})", 1)
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], TextType.TEXT))

            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            remaining_text = parts[1]

        if remaining_text != "":
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes

def text_to_textnodes(text: str) -> list[TextNode]:
    result = [TextNode(text, TextType.TEXT)]
    result = split_nodes_image(result)
    result = split_nodes_link(result)
    result = split_nodes_delimiter(result, "**", TextType.BOLD)
    result = split_nodes_delimiter(result, "_", TextType.ITALIC)
    result = split_nodes_delimiter(result, "`", TextType.CODE)
    return result

def markdown_to_blocks(markdown: str) -> list[str]:
    result = []
    blocks = markdown.split("\n\n")
    for block in blocks:
        block = block.strip()
        if block == "":
            continue
        result.append(block)
    return result

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered list"

def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")

    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING

    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    ordered_list_numbers = []
    for line in lines:
        match = re.match(r"^(\d+)\. ", line)
        if match is None:
            break
        ordered_list_numbers.append(int(match.group(1)))

    if ordered_list_numbers == list(range(1, len(lines) + 1)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown: str) -> HTMLNode:

    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            children.append(paragraph_to_html_node(block))
        elif block_type == BlockType.HEADING:
            children.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            children.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            children.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(unorderedlist_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(orderedlist_to_html_node(block))

    return ParentNode("div", children)

################



def text_to_children(text: str) -> list[HTMLNode]:
    return [
        text_node_to_html_node(node)
        for node in text_to_textnodes(text)
    ]

def paragraph_to_html_node(block: str) -> HTMLNode:
    block = block.replace("\n", " ")
    children = text_to_children(block)
    return ParentNode("p", children)

def heading_to_html_node(block: str) -> HTMLNode:
    counter = 0
    for c in block:
        if c == "#":
            counter +=1
        else:
            break
    block = block[counter + 1:]
    children = text_to_children(block)
    return ParentNode(f'h{counter}', children)

def code_to_html_node(block: str) -> HTMLNode:
    lines = block.split("\n")
    code = "\n".join(lines[1:-1]) + "\n"
    return ParentNode("pre", [LeafNode("code", code)])

def quote_to_html_node(block: str) -> HTMLNode:
    quote_text = " ".join(line[1:].lstrip() for line in block.split("\n"))
    children = text_to_children(quote_text)
    return ParentNode("blockquote", children)

def unorderedlist_to_html_node(block: str) -> HTMLNode:
    items = []

    for line in block.split("\n"):
        item_text = line[2:]
        items.append(ParentNode("li", text_to_children(item_text)))

    return ParentNode("ul", items)

def orderedlist_to_html_node(block: str) -> HTMLNode:
    items = []

    for line in block.split("\n"):
        item_text = re.sub(r"^\d+\. ", "", line)
        items.append(ParentNode("li", text_to_children(item_text)))

    return ParentNode("ol", items)