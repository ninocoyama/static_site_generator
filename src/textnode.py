from enum import Enum
from htmlnode import LeafNode


class TextType(Enum):
    TEXT = "plain text type"
    BOLD = "bold text type"
    ITALIC = "italic text type"
    CODE = "code text type"
    LINK = "link type"
    IMAGE = "image type"

class TextNode():
    def __init__(self, text: str, text_type: TextType, url = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if (
            self.text == other.text 
            and self.text_type == other.text_type 
            and self.url == other.url
        ):
            return True
        return False


    def __repr__(self):
        return (f"TextNode({self.text}, {self.text_type.value}, {self.url})")

#handle each type of the TextType enum
def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception("Text type not valid")