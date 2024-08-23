from functools import lru_cache
from . import config

@lru_cache
def get_settings():
    return config.Settings()

def get_noun_word(words: list, delimiter_text:str, noun_type:str, stop_words:list[str]):
    noun_words = []
    for text_split in words:
        text_split = text_split
        text_and_type = text_split.split(delimiter_text)
        type = text_and_type.pop()
        if type == noun_type:
            text = text_and_type.pop()
            # Nếu từ không phải hư từ thì đưa vào tập V
            if text.lower() not in stop_words:
                noun_words.append(text.lower())
    return noun_words