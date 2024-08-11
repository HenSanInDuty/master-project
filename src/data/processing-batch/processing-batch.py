import os
import subprocess
import pandas as pd
from subprocess import Popen

working_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

data_dir = working_dir + "\\src\\data"
data_preprocess_path = data_dir + "\\data_crawl.json"
bat_file_path = data_dir + "\\processing-batch\\Tokenizer.bat"
jar_file_path = data_dir + "\\processing-batch\\JVnTextPro-3.0.3-executable.jar"

#Read file
df = pd.read_json(data_preprocess_path, encoding="utf8", orient='records').drop_duplicates()

topics = set(df['topic'])

for topic in topics:
    # Get data with topic
    data = df[df['topic'] == topic]

    # Concat all content
    content = "Nhan Tran Trong"
    for row in data:
        print(row)
        #content += row['content']
    input_file_name = f"{topic}.txt"
        
    # Write content to file for Tagging    
    with open(input_file_name, "w") as file:
        file.write(content)
    
    
    # Tagging 
    p = subprocess.call([bat_file_path, jar_file_path, input_file_name])
    
    