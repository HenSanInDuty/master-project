import math
import os
from fastapi import Depends
from typing_extensions import Annotated
import pandas as pd
import subprocess
import tempfile
from functools import lru_cache

from . import models
from . import config


@lru_cache
def get_settings():
    return config.Settings()

def get_working_dir():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def get_noun_word(words: list, pos_tool: str, stop_words:list[str]) -> list[str]:
    '''
    Get noun word in list word
    
    Param
    --------------------------------
    words: list word
    delimiter_text:
    noun_type: type of noun at pos tool
    stop_words
    
    Return
    -------------------------------
    List noun word
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
    Get feature of POS tool
    
    Param
    ------------------------------------
    pos_tool: name of pos tool
    
    Return
    ------------------------------------
    Features of POS tool
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

def pos_tag_document(preprocess_documents:dict, pos_tool: str) -> dict:
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
    tagging_documents = {}
    options_tool = get_feature_pos_tools(pos_tool)
    
    if options_tool is None:
        raise Exception("Không tìm thấy tool này")
    
    for topic in preprocess_documents.keys():
        match options_tool['tool_type']:
            case 'jar':
                jar_file = get_working_dir() + setting.tool_path + f'{pos_tool}.jar'
                # Write content to file for Tagging
                with tempfile.TemporaryFile(delete_on_close=False) as fp:
                    content = f'{preprocess_documents[f'{topic}']}'.encode(encoding="utf-8")
                    fp.write(content)
                    fp.close()
                    # Tagging 
                    subprocess.call(['java', '-jar', jar_file, '-senseg', '-wordseg' ,'-postag' ,'-input', fp.name])
                    
                    with open(f'{fp.name}{options_tool['file_extension']}', mode='r', encoding="utf-8") as f:
                        tagging_documents[f'{topic}'] = f.read()
            case _:
                raise Exception("Chưa hỗ trợ định dạng này")
    return tagging_documents

def train_topic_model(tagged_model: dict, option_trainning: models.OptionTrainning, stop_words: list[str]) -> dict:
    '''
    Hàm train topic model
    
    Param
    ---------------------------------------------------
    tagged_model: Kết quả trả về sau khi chạy tool gán nhãn từ loại
    option_trainning: Tuỳ chỉnh huấn luyện ở GUI
    stop_words: Danh sách hư từ
    
    Return
    ---------------------------------------------------
    Topic model
    {
        'Topic': [core_word]
    }
    '''
    topics = tagged_model.keys()
    
    S = {f"{topic}":[] for topic in topics}
    V = {f"{topic}":[] for topic in topics}
    N = {}
    n = {}
    
    # Xử lý lấy tất cả danh từ đưa vào tập V
    for topic in topics:
        text = tagged_model[f'{topic}']
        # Xoá các ký tự xuống dòng
        text = text.replace("\n", " ")
        
        # Tách các từ
        text_splits = text.split(" ")
        
        # Tách câu
        sentences_splits = text.split("./.")
        
        # Đưa các từ thuộc danh từ vào tập V
        V[f'{topic}'] = get_noun_word(text_splits, option_trainning.pos_tool, stop_words)
        
        # Đưa các câu vào tập S
        for sentences_split in sentences_splits:
            S[f'{topic}'].append(sentences_split)
    
    # Tìm kiếm từ core cho mỗi chủ đề
    for topic in topics:
        n = {}
        for text in V[f'{topic}']:
            if text in n.keys():
                n[f"{text}"] += 1
            else:
                n[f"{text}"] = 1
        
        N[f'{topic}'] = [max(n, key=n.get), n[max(n, key=n.get)]]

    # Cập nhật lại V cho các chủ đề
    V = {f"{topic}":[] for topic in topics}
    for topic in topics:
        n = {}
        
        # Lấy ra từ core
        core_word = N[f'{topic}']
        
        for sentence in S[f'{topic}']:
            # Tách các từ
            words = sentence.split(" ")
            
            # Lấy ra các danh từ
            noun_words = get_noun_word(words, option_trainning.pos_tool, stop_words)
            # Nếu như core word có mặt trong câu thì cộng lại số lượng những danh từ trong đó
            if core_word[0] in noun_words:
                for noun_word in noun_words:
                    if noun_word in n.keys():
                        n[f"{noun_word}"] += 1
                    else:
                        n[f"{noun_word}"] = 1
            
        # Nếu trong 1 câu cùng xuất hiện từ chủ đề và 1 danh từ thì đưa danh từ vào tập chủ đề đó dựa trên threshold
        for word, frequency in n.items():
            if frequency/core_word[1] > option_trainning.threshold_core_word:
                V[f'{topic}'].append([word.lower(), frequency])
    
    return V
    
def calculate_word_similarity(topic_model: dict, method: str, tagged_document: dict, trainning_option: models.OptionTrainning, stop_words: list[str]) -> dict:
    '''
    Hàm tính độ tương tự của từ
    
    Param
    -------------------------------
    topic_model: mô hình chủ đề
    method: phương thức để tính độ tương tự của từ
    tagged_document: văn bản đã được gán nhãn từ loại
    stop_words: danh sách hư từ
    
    Return
    -------------------------------
    Trả về độ tương tự của từ
    '''
    
    match method:
        case 'PMI':
            topics = topic_model.keys()
            # Lấy ra các core word từ topic model
            core_word = []
            for key, items in topic_model.items():
                for item in items:
                    core_word.append(item[0])
            S = []
                    
            # Lấy tất cả các câu đưa vào tập S
            for topic in topics:
                text = tagged_document[f'{topic}']
                # Xoá các ký tự xuống dòng
                text = text.replace("\n", " ")
                
                # Tách câu
                sentences_splits = text.split("./.")
                
                # Đưa các câu vào tập S
                S = S + sentences_splits
                
                # Tính toán số lần xuất hiện của các cặp từ 
                pair_noun = {}
                count_noun = {}
                count_all_word = 0
                for sentence in S:
                    words_in_sen = sentence.split(" ")
                    noun_word = get_noun_word(words_in_sen, trainning_option.pos_tool, stop_words)
                    noun_word.sort()
                    
                    # Tính số lượng các từ chủ đề trong tập huấn luyện
                    count_all_word += len(noun_word)
                    for i in range(len(noun_word)):
                        
                        # Tính số lần xuất hiện của từ
                        if noun_word[i] not in count_noun.keys():
                            count_noun[f'{noun_word[i]}'] = 1
                        else:
                            count_noun[f'{noun_word[i]}'] += 1
                        
                        for j in range(i, len(noun_word)):
                            if noun_word[i] != noun_word[j]:
                                # Tính số lần xuất hiện của các cặp từ
                                word_pair = noun_word[i] + " " + noun_word[j]
                                if word_pair not in pair_noun.keys():
                                    pair_noun[f'{word_pair}'] = 1
                                else:
                                    pair_noun[f'{word_pair}'] += 1

                count_noun['count_all_word'] = count_all_word
                
                # Tính toán PMI cho các từ
                PMI = {}
                count_all_word = count_noun['count_all_word']
                for key, item in pair_noun.items():
                    word = key.split(" ")
                    p_pair = pair_noun[f'{key}'] / count_all_word
                    p_word1 = count_noun[f'{word[0]}'] / count_all_word
                    p_word2 = count_noun[f'{word[1]}'] / count_all_word
                    
                    pmi = math.log2(p_pair / (p_word1 * p_word2))
                    if pmi > 0:
                        PMI[f'{key}'] = pmi
                        
                return PMI
        case _:
            raise Exception(f"Chưa hỗ trợ phương thức tính {method} này")