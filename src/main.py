from textnode import TextNode
from textnode import TextType

def main():
    textnode = TextNode("Text test", TextType.BOLD, "http://google.com")
    print(textnode)


main()