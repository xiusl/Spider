# coding=utf-8
# author:xsl

def fix_text(text):
    if isinstance(text, str):
        return text.strip()
    t = ''.join(text)
    return t.strip()
