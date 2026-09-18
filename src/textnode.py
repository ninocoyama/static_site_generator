from enum import Enum


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