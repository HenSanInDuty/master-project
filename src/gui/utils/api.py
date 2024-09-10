import requests
from . import contants

async def get_pos_tools():
    return requests.request(method=contants.get_pos_tools['method'], url=contants.get_pos_tools['url']).json()

async def get_word_similarity_tools():
    return requests.request(method=contants.get_word_similarity_tools['method'], url=contants.get_word_similarity_tools['url']).json()

async def trainning(document_uploaded_json, stop_word_text_file, trainning_option):
    return requests.request(method=contants.trainning['method'], 
                            url=contants.trainning['url'], 
                            params=trainning_option, 
                            files={
                                'documents': document_uploaded_json,
                                'stop_words': stop_word_text_file
                            }
                            ).json()

async def inference(document_uploaded_json, topic_model, trainning_option):
    return requests.request(method=contants.inference['method'], 
                            url=contants.inference['url'], 
                            params=trainning_option, 
                            files={
                                'documents': document_uploaded_json,
                                'models': topic_model
                            }
                            ).json()
    
async def evaluate(document_uploaded_json, topic_model, trainning_option):
    return requests.request(method=contants.evaluate['method'], 
                            url=contants.evaluate['url'], 
                            params=trainning_option, 
                            files={
                                'test_documents': document_uploaded_json,
                                'models': topic_model
                            }
                            ).json()
    
async def summary(document_uploaded_json, trainning_option):
    files = []
    for file in document_uploaded_json:
        files.append(('documents', file))
    return requests.request(method=contants.summary['method'], 
                            url=contants.summary['url'], 
                            params=trainning_option, 
                            files = files
                            ).json()