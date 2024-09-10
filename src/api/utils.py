import os
import pandas as pd
import subprocess
import tempfile

from functools import lru_cache
from . import config

@lru_cache
def get_settings():
    return config.Settings()

def get_working_dir():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def get_noun_word(words: list, pos_tool: str, stop_words:list[str]) -> list[str]:
    '''
    Lấy danh từ trong danh sách từ
    
    Param
    --------------------------------
    words: danh sách từ
    delimiter_text: dấu phân cách của công cụ gán nhãn từ loại
    noun_type: từ đánh dấu danh từ của công cụ gán nhãn từ loại
    stop_words: danh sách hư từ
    
    Return
    -------------------------------
    Trả về danh sách danh từ trong danh sách từ
    '''
    
    option_pos_tool = get_feature_pos_tools(pos_tool)
    delimiter_text = option_pos_tool['delimiter']
    noun_type = option_pos_tool['noun_type']
    noun_words = []
    for text_split in words:
        text_split = text_split
        text_and_type = text_split.split(delimiter_text)
        type = text_and_type.pop()
        if type == noun_type:
            text = text_and_type.pop()
            if text.lower() not in stop_words:
                noun_words.append(text.lower())
    return noun_words

def get_feature_pos_tools(pos_tool: str) -> dict | None:
    '''
    Lấy ra những thông tin liên quan đến công cụ gán nhãn
    
    Param
    ------------------------------------
    pos_tool: tên của công cụ gán nhãn
    
    Return
    ------------------------------------
    Các thông tin của công cụ
    '''
    
    match pos_tool:
        case "JVnTextPro":
            return {
                'delimiter': '/',
                'noun_type': 'N',
                'file_extension': '.pro',
                'tool_type': 'jar'
            }
        case _:
            return None

def pre_processing_document(documents: pd.DataFrame) -> dict:
    '''
    Tiền xử lý tập văn bản
    
    Param
    -------------------------
    documents: Tập văn bản được đọc từ controller
    
    Return
    -------------------------
    Văn bản sau khi xử lý
    '''
    
    #Read file
    topics = set(documents['topic'])
    preprocess_document = {}
    for topic in topics:
        # Get data with topic
        data = documents[documents['topic'] == topic]
        # Concat all content
        content = ""
        for row in data['content']:
            content += row
        content = content.replace("\n", " ")
        preprocess_document[f'{topic}'] = content
    
    return preprocess_document

def pos_tag_document_with_topic(preprocess_documents:dict, pos_tool: str) -> dict:
    '''
    Gán từ loại cho văn bảng đã tiền xử lý
    
    Param
    -----------------------------------
    preprocess_documents: Văn bản đã tiền xử lý
    pos_tool: tên của tool gán nhãn từ loại
    
    Return
    -----------------------------------
    Văn bản sau khi gán nhãn từ loại
    '''
    
    tagging_documents = {}
    options_tool = get_feature_pos_tools(pos_tool)
    
    if options_tool is None:
        raise Exception("Không tìm thấy tool này")
    
    for topic in preprocess_documents.keys():
        tagging_documents[f'{topic}'] = pos_tag_document(f'{preprocess_documents[f'{topic}']}', pos_tool)
    
    return tagging_documents

def pos_tag_document(preprocess_documents:str, pos_tool: str) -> str:
    '''
    Gán từ loại cho văn bảng đã tiền xử lý
    
    Param
    -----------------------------------
    preprocess_documents: Văn bản đã tiền xử lý
    pos_tool: tên của tool gán nhãn từ loại
    
    Return
    -----------------------------------
    Văn bản sau khi gán nhãn từ loại
    '''
    
    setting = get_settings()
    tagging_document = ''
    options_tool = get_feature_pos_tools(pos_tool)
    
    if options_tool is None:
        raise Exception("Không tìm thấy tool này")
    
    match options_tool['tool_type']:
        case 'jar':
            jar_file = get_working_dir() + setting.tool_path + f'{pos_tool}.jar'
            # Write content to file for Tagging
            with tempfile.TemporaryFile(delete_on_close=False) as fp:
                content = preprocess_documents.encode(encoding="utf-8")
                fp.write(content)
                fp.close()
                # Tagging 
                subprocess.call(['java', '-jar', jar_file, '-senseg', '-wordseg' ,'-postag' ,'-input', fp.name])
                with open(f'{fp.name}{options_tool['file_extension']}', mode='r', encoding="utf-8") as f:
                    tagging_document = f.read()
        case _:
            raise Exception("Chưa hỗ trợ định dạng này")
    return tagging_document

def get_model(model_name:str) -> dict:
    setting = get_settings()
    models_dir = get_working_dir() + setting.trained_model_path
    
    