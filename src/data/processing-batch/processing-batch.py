import os
import subprocess
import pandas as pd
from subprocess import Popen

working_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

data_dir = working_dir + "\\src\\data"
data_preprocess_path = data_dir + "\\data_crawl.json"
# dic_path = working_dir + "\\src\\data\\processing-batch\\VDic\\VDic_uni.txt"

# Get Dic
# dic = pd.read_csv(dic_path, delimiter = "\t\t", header=None)
# print(dic)

#Read file
# df = pd.read_json(data_preprocess_path, encoding="utf8", orient='records').drop_duplicates()

# print(df)
bat_file_path = data_dir + "\\processing-batch\\Tokenizer.bat"
p = subprocess.run([bat_file_path], capture_output=True, text=True)

# Run tokenizer
# spark-submit ./src/data/processing-batch/vlp-master/tok/target/scala-2.12/tok.jar in.txt