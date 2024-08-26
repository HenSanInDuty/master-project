import requests
from . import contants

async def get_pos_tools():
    return requests.request(method=contants.get_pos_tools['method'], url=contants.get_pos_tools['url']).json()

async def get_word_similarity_tools():
    return requests.request(method=contants.get_word_similarity_tools['method'], url=contants.get_word_similarity_tools['url']).json()

async def trainning():
    return requests.request(method=contants.trainning['method'], url=contants.trainning['url']).json()