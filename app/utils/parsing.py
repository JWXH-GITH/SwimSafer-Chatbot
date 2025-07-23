import re

def clean_text(text: str) -> str:
    """
    Cleans and normalizes text by removing extra whitespace and newlines.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
