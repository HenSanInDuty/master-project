from pydantic import BaseModel

class OptionTrainning(BaseModel):
    pos_tool: str = ''
    threshold_core_word: float = 0.0
    similarity_calculation_method: str = ''
    r_threshold: float = 0.4
    alpha: float = 0.3
    model: str = ''

class Sentence():
    '''Class câu'''
    content: str
    content_original: str
    position: int
    topic: str
    weight: float
    document_position: int
    
    def __init__(self, content:str, position:int, topic:str):
        self.content = content
        self.position = position
        self.topic = topic
        self.weight = 0.0
        
        # Xoá các loại từ và dấu _
        original_sentence = " "
        for word in content.split(" "):
            original_sentence += word.split("/")[0].replace('_', ' ') + ' '
        self.content_original = original_sentence
    
    def set_topic(self, topic:str):
        self.topic = topic
    
    def set_weight(self, weight: float):
        self.weight = weight
    
    def set_document_position(self, document_position: int):
        self.document_position = document_position
    
class Document():
    '''Class văn bản'''
    sentences: list[Sentence]
    topic: str
    weight: float
    position: int
    
    def __init__(self, sentences: list, topic: str, position: int):
      self.sentences = sentences
      self.topic = topic
      self.weight = 0
      self.position = position
    
    def add_sentence(self, sentence: Sentence):
        self.sentences.append(sentence)
    
    def get_document(self):
        document = ''
        for sentence in self.sentences:
            document += sentence.content + './.'
        
        return document
    
    def set_topic(self, topic: str):
        self.topic = topic
    
    def set_weight(self, weight: float):
        self.weight = weight
    
    def apply_weight_for_sentences(self, weight_sentences: list[dict]):
        for i in range(len(self.sentences)):
            self.sentences[i].set_weight(weight_sentences[i]['weight'])
        
        self.weight = weight_sentences[len(weight_sentences) - 1]
    
    def apply_document_weight_for_sentences(self):
        for i in range(len(self.sentences)):
            self.sentences[i].set_weight(self.sentences[i].weight + self.sentences[i].weight * self.weight)

class TopicModel():
    '''Class cho mô hình chủ đề'''
    topics: list[str]
    core_words: dict
    
    def __init__(self):
      self.topics = []
      self.core_words = []
    
    def add_topic(self, topic:str):
        self.topics.append(topic)
    
    def add_topics(self, topic:list[str]):
        self.topics.append(**topic)
    
    def add_core_word_to_topic(self, core_word: str, topic: str):
        if topic not in self.core_words.keys():
            self.core_words[f'{topic}'] = [core_word]
        else:
            self.core_words[f'{topic}'].append(core_word)
