import datetime
import json
import os
import tempfile

from functools import lru_cache
from sklearn.model_selection import train_test_split

from fastapi import Depends, FastAPI, UploadFile
from pandas import read_json
from typing_extensions import Annotated
from . import utils, models, config
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

@app.get("/pos_tools")
async def get_pos_tools():
    return ["JVnTextPro"]

@app.get("/word_similarity_tools")
async def word_similarity_tools():
    return ["PMI"]

@app.post("/trainning/")
async def trainning(documents: UploadFile, stop_words: UploadFile | None, options: models.OptionTrainning = Depends()):
    # Tiền xử lý
    df = read_json(documents.file, encoding="utf8", orient='records').drop_duplicates()
    X_train, X_test = train_test_split(df, test_size=0.33, random_state=42)
    pre_processing_document = utils.pre_processing_document(X_train)
    
    # Xử lý tập tin hư từ
    list_stop_word = []
    if stop_words is not None:
        stop_word_file = stop_words.file.read().decode()
        list_stop_word = stop_word_file.split("\n")
        
    # Huấn luyện mô hình chủ đề
    tagged_model = utils.pos_tag_document(pre_processing_document, options.pos_tool)
    topic_model = utils.train_topic_model(tagged_model, options, list_stop_word)
    
    # Tính toán độ tương tự của từ
    word_similarity = utils.calculate_word_similarity(topic_model, options.similarity_calculation_method, tagged_model, options, list_stop_word)
    
    # Trả về định dạng dict
    json_model =  {
        'topic_model': topic_model,
        'word_similarity': word_similarity
    }
    
    # Đánh giá mô hình
        
    return JSONResponse(json_model)

@app.post("/inference/")
async def inference(options: models.OptionTrainning):
    return []

@app.post("/evaluate")
async def evaluate():
    return []