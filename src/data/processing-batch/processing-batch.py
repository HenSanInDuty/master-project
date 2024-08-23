import os
import subprocess
import pandas as pd

working_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

data_dir = working_dir + "\\src\\data"
data_preprocess_path = data_dir + "\\data_crawl.json"
bat_file_path = data_dir + "\\processing-batch\\Tokenizer.bat"
jar_file_path = data_dir + "\\processing-batch\\JVnTextPro-3.0.3-executable.jar"
stop_word_path = data_dir + "\\processing-batch\\vietnamese-stopwords-dash.txt"
    
def handle_stop_word():
    stop_word_file = open(stop_word_path, "r", encoding="utf-8")
    stop_words = stop_word_file.read()
    stop_words = stop_words.split("\n")

if __name__ == "__main__":
    #Read file
    df = pd.read_json(data_preprocess_path, encoding="utf8", orient='records').drop_duplicates()
    topics = set(df['topic'])

    for topic in topics:
        # Get data with topic
        data = df[df['topic'] == topic]
        # Concat all content
        content = ""
        for row in data['content']:
            content += row
        content = content.replace("\n", " ")
        input_file_name = data_dir + f"\\processing-batch\\data-process\\{topic}.txt"
            
        # Write content to file for Tagging    
        with open(input_file_name, "w", encoding="utf-8") as file:
            file.write(content)
        
        # Tagging 
        p = subprocess.call([bat_file_path, jar_file_path, input_file_name])