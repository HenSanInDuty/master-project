API_host = 'http://localhost:8000/'

# NLP POS
get_pos_tools = {
    'method': 'GET',
    'url': API_host + 'pos_tools'
}

# NLP similarity tools
get_word_similarity_tools = {
    'method': 'GET',
    'url': API_host + 'word_similarity_tools'
}

# NLP Trainning topic model
trainning = {
    'method': 'POST',
    'url': API_host + 'trainning'
}

inference = {
    'method': 'POST',
    'url': API_host + 'inference'
}

evaluate = {
    'method': 'POST',
    'url': API_host + 'evaluate'
}