import json
from sklearn.model_selection import train_test_split

from fastapi import Depends, FastAPI, UploadFile
from pandas import read_json
from . import utils, models, evaluation, train, inference
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/pos_tools")
async def get_pos_tools():
    return ["JVnTextPro"]


@app.get("/word_similarity_tools")
async def word_similarity_tools():
    return ["PMI"]


@app.post("/trainning/")
async def trainning(
    documents: UploadFile,
    stop_words: UploadFile | None,
    options: models.OptionTrainning = Depends(),
):
    # Tiền xử lý
    df = read_json(documents.file, encoding="utf8", orient="records").drop_duplicates()
    df = df[df["content"] != ""]

    # X_train, X_test = train_test_split(df, test_size=0.33, random_state=42, stratify=df['topic'])
    X_train, X_test = train_test_split(df, test_size=0.33, random_state=42)
    pre_processing_document = utils.pre_processing_document(X_train)

    # Xử lý tập tin hư từ
    list_stop_word = []
    if stop_words is not None:
        stop_word_file = stop_words.file.read().decode()
        list_stop_word = stop_word_file.split("\n")

    # Huấn luyện mô hình chủ đề
    tagged_model = utils.pos_tag_document_with_topic(
        pre_processing_document, options.pos_tool
    )
    topic_model = train.train_topic_model(tagged_model, options, list_stop_word)

    # Tính toán độ tương tự của từ
    word_similarity = train.calculate_word_similarity(
        topic_model,
        options.similarity_calculation_method,
        tagged_model,
        options,
        list_stop_word,
    )

    # Trả về định dạng dict
    json_model = {
        "topic_model": topic_model,
        "word_similarity": word_similarity,
        "stop_words": list_stop_word,
    }

    # Đánh giá mô hình
    evaluate = {
        "ROUGE-1":[],
        "ROUGE-2":[],
        "ROUGE-L":[],
        "BertScore":[]
    }

    X_test = train.split_document(X_test, 10)
    print("Evaluating..............................")
    for documents in X_test:
        # Thực hiện tóm tắt một cụm văn bản
        documents = documents.to_dict("records")
        summary_document, _, _ = inference.summary_cluster_document(
            documents, topic_model, word_similarity, options, list_stop_word
        )
        # Kết quả tóm tắt của toàn bộ văn bản
        summary_document_str = inference.concat_list_summary_sentences(summary_document)

        # Kết hợp các văn bản lại với nhau cho ra văn bản gốc
        list_content = [document["content"] for document in documents]
        original_cluster_document = "".join(list_content)

        # Đánh giá theo độ đo ROUGE và BertScore
        rouge_evaluation = evaluation.ROUGE_evaluate(original_cluster_document, summary_document_str)
        evaluate["ROUGE-1"].append(rouge_evaluation["rouge-1"]["f"])
        evaluate["ROUGE-2"].append(rouge_evaluation["rouge-2"]["f"])
        evaluate["ROUGE-L"].append(rouge_evaluation["rouge-l"]["f"])
        evaluate["BertScore"].append(
            evaluation.BertScore_evaluate(
                original_cluster_document, summary_document_str
            )
        )

    json_model["evaluate"] = evaluation.return_evaluation_for_GUI(evaluate)
    return JSONResponse(json_model)


@app.post("/inference/")
async def inference_api(
    documents: UploadFile, models: UploadFile | None, options: models.OptionTrainning = Depends()
):
    # Tiền xử lý
    df = read_json(documents.file, encoding="utf8", orient="records").drop_duplicates()
    df = df[df["content"] != ""]

    # Đọc file model
    models_json = json.load(models.file)

    # Thêm các thông số huấn luyện
    options.similarity_calculation_method = models_json['word_similarity']['type']
    list_stop_word = models_json['stop_words']
    word_similarity = models_json['word_similarity']
    topic_model = models_json['topic_model']
    print(models_json['word_similarity']['type'])
    
    # Kết quả trả về có dạng
    result = {
        "summary_document": "", # văn bản sau khi tóm tắt
        "sentences": [], # mỗi phần tử là một câu
        "sentences_weight": [], # mỗi phần tử có dạng số
        "sentences_similarity": [], # mỗi phần tử có dạng [index_câu, index_câu, độ tương đồng]
        "metric_info": {}, # các độ đo dùng để đánh giá
        "number_sentence": 0 # số lượng câu tóm tắt
    }
    evaluate = {}
    # Thực hiện tóm tắt một cụm văn bản
    print("Sumarizing..............................")
    documents = df.to_dict("records")
    summary_document, sentence_similarity, all_sentences = inference.summary_cluster_document(
        documents, topic_model, word_similarity, options, list_stop_word
    )
    sorted_summary_document = sorted(summary_document, key=lambda x:x.position)
    # Kết quả tóm tắt của toàn bộ văn bản
    summary_document_str = inference.concat_list_summary_sentences(sorted_summary_document, with_position = True)
    
    # Kết hợp các văn bản lại với nhau cho ra văn bản gốc
    list_content = [document["content"] for document in documents]
    original_cluster_document = "".join(list_content)

    # Đánh giá theo độ đo ROUGE và BertScore
    rouge_evaluation = evaluation.ROUGE_evaluate(original_cluster_document, summary_document_str)
    
    evaluate["ROUGE-1"] = [rouge_evaluation["rouge-1"]["f"]]
    evaluate["ROUGE-2"] = [rouge_evaluation["rouge-2"]["f"]]
    evaluate["ROUGE-L"] = [rouge_evaluation["rouge-l"]["f"]]
    
    evaluate["BertScore"] =  [evaluation.BertScore_evaluate(
            original_cluster_document, summary_document_str
        )]
    
    # evaluate["Gemini-Review"] = ["Tương đối ngon"]
    
    # Kết quả trả về
    result['summary_document'] = summary_document_str
    result['sentences'] = [sentence.content_original for sentence in all_sentences]
    result['sentences_weight'] = [sentence.weight for sentence in all_sentences]
    result["metric_info"] = evaluate
    result['number_sentence'] = len(summary_document)
    
    for i in range(len(all_sentences) - 1):
        for j in range(i+1, len(all_sentences)):
            key = f'{all_sentences[i].position} {all_sentences[j].position}'
            similarity = [i, j, sentence_similarity[f'{key}']]
            result['sentences_similarity'].append(similarity)
    return JSONResponse(result)


@app.post("/evaluate")
async def evaluate_api():
    return []
