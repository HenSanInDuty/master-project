from functools import lru_cache

from fastapi import Depends, FastAPI
from typing_extensions import Annotated

from . import config

app = FastAPI()


@lru_cache
def get_settings():
    return config.Settings()

@app.get("pos_tools")
def get_pos_tools():
    return ["JVNPro"]

@app.get("word_similarity_tools")
def word_similarity_tools():
    return ["PMI"]

@app.get("trainning")
def trainning():
    # Pre-processing
    # Trainning topic model
    # Trainning similarity
    # Return json model
    return ["JVNPro"]