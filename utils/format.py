import zhconv
import unicodedata

def normalize_str(string: str) -> str:
    string = unicodedata.normalize('NFKC', string)
    string = string.strip()
    string = string.lower()
    string = zhconv.convert(string, 'zh-hans')
    return string