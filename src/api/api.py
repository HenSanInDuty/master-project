import json
import pandas as pd
from sklearn.model_selection import train_test_split

from fastapi import Depends, FastAPI, UploadFile
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
    df = pd.read_json(documents.file, encoding="utf8", orient="records").drop_duplicates()
    df = df[df["content"] != ""]

    pre_processing_document = utils.pre_processing_document(df)

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

    return JSONResponse(json_model)


@app.post("/inference/")
async def inference_api(
    documents: UploadFile,
    models: UploadFile | None,
    options: models.OptionTrainning = Depends(),
):
    # Tiền xử lý
    df = pd.read_json(documents.file, encoding="utf8", orient="records").drop_duplicates()
    df = df[df["content"] != ""]

    # Đọc file model
    models_json = json.load(models.file)

    # Thêm các thông số huấn luyện
    options.similarity_calculation_method = models_json["word_similarity"]["type"]
    list_stop_word = models_json["stop_words"]
    word_similarity = models_json["word_similarity"]
    topic_model = models_json["topic_model"]
    print(models_json["word_similarity"]["type"])

    # Kết quả trả về có dạng
    result = {
        "summary_document": "",  # văn bản sau khi tóm tắt
        "sentences": [],  # mỗi phần tử là một câu
        "sentences_weight": [],  # mỗi phần tử có dạng số
        "sentences_similarity": [],  # mỗi phần tử có dạng [index_câu, index_câu, độ tương đồng]
        "metric_info": {},  # các độ đo dùng để đánh giá
        "number_sentence": 0,  # số lượng câu tóm tắt
    }
    evaluate = {}
    # Thực hiện tóm tắt một cụm văn bản
    print("Sumarizing..............................")
    documents = df.to_dict("records")
    summary_document, sentence_similarity, all_sentences = (
        inference.summary_cluster_document(
            documents, topic_model, word_similarity, options, list_stop_word
        )
    )
    sorted_summary_document = sorted(summary_document, key=lambda x: x.position)
    # Kết quả tóm tắt của toàn bộ văn bản
    summary_document_str = inference.concat_list_summary_sentences(
        sorted_summary_document, with_position=True
    )

    # Kết hợp các văn bản lại với nhau cho ra văn bản gốc
    list_content = [document["content"] for document in documents]
    original_cluster_document = "".join(list_content)

    # Đánh giá theo độ đo ROUGE và BertScore
    rouge_evaluation = evaluation.ROUGE_evaluate(
        original_cluster_document, summary_document_str
    )

    evaluate["ROUGE-1"] = [rouge_evaluation["rouge-1"]["f"]]
    evaluate["ROUGE-2"] = [rouge_evaluation["rouge-2"]["f"]]
    evaluate["ROUGE-L"] = [rouge_evaluation["rouge-l"]["f"]]

    evaluate["BertScore"] = [
        evaluation.BertScore_evaluate(original_cluster_document, summary_document_str)
    ]

    # evaluate["Gemini-Review"] = ["Tương đối ngon"]

    # Kết quả trả về
    result["summary_document"] = summary_document_str
    result["sentences"] = [sentence.content_original for sentence in all_sentences]
    result["sentences_weight"] = [sentence.weight for sentence in all_sentences]
    result["metric_info"] = evaluate
    result["number_sentence"] = len(summary_document)

    for i in range(len(all_sentences) - 1):
        for j in range(i + 1, len(all_sentences)):
            key = f"{all_sentences[i].position} {all_sentences[j].position}"
            similarity = [i, j, sentence_similarity[f"{key}"]]
            result["sentences_similarity"].append(similarity)
    return JSONResponse(result)


@app.post("/evaluate/")
async def evaluate_api(
    test_documents: UploadFile,
    models: UploadFile | None,
    options: models.OptionTrainning = Depends(),
):
    # Đọc file test documents
    test_documents = json.load(test_documents.file)
    cluster_document = [test_document["documents"] for test_document in test_documents]
    input_summary_cluster_document = [
        test_document["summary_content"] for test_document in test_documents
    ]

    # Đọc file model
    models_json = json.load(models.file)

    # Thêm các thông số huấn luyện
    options.similarity_calculation_method = models_json["word_similarity"]["type"]
    list_stop_word = models_json["stop_words"]
    word_similarity = models_json["word_similarity"]
    topic_model = models_json["topic_model"]

    # Đánh giá mô hình
    numbers_of_summary_version = len(input_summary_cluster_document[0])
    evaluations = [{
                    "ROUGE-1":[],
                    "ROUGE-2":[],
                    "ROUGE-L":[],
                    "BertScore":[]
                } for _ in range(numbers_of_summary_version)]
    print("Evaluating..............................")
    for i in range(len(input_summary_cluster_document)):
        documents = cluster_document[i]

        # Thực hiện tóm tắt 1 cụm văn bản
        summary_document, _, _ = inference.summary_cluster_document(
            documents, topic_model, word_similarity, options, list_stop_word
        )
        # Kết quả tóm tắt của toàn bộ văn bản
        summary_document_str = inference.concat_list_summary_sentences(summary_document)

        # Lấy ra văn bản tóm tắt
        for index, summary_documents in enumerate(input_summary_cluster_document[i]):
            # Đánh giá theo độ đo ROUGE và BertScore
            rouge_evaluation = evaluation.ROUGE_evaluate(
                summary_documents, summary_document_str
            )
            evaluations[index]["ROUGE-1"].append(rouge_evaluation["rouge-1"]["f"])
            evaluations[index]["ROUGE-2"].append(rouge_evaluation["rouge-2"]["f"])
            evaluations[index]["ROUGE-L"].append(rouge_evaluation["rouge-l"]["f"])
            evaluations[index]["BertScore"].append(evaluation.BertScore_evaluate(
                summary_documents, summary_document_str
            ))

    evaluations = evaluation.return_evaluation_for_GUI(evaluations)
    return JSONResponse(evaluations)

@app.post("/summary/")
async def summary_api(
    documents: list[UploadFile],
    options: models.OptionTrainning = Depends(),
):
    # Tiền xử lý
    document_list = []
    for document in documents:
        document_list.append({
            "content": document.file.read().decode("utf-8"),
            "topic": ""
        })
    
    # Đọc file model
    model_path = utils.get_model(options.choice_model)
    with open(model_path, "r", encoding="utf8") as file:
        models_json = json.load(file)
    
    # Thêm các thông số huấn luyện
    options.similarity_calculation_method = models_json["word_similarity"]["type"]
    list_stop_word = models_json["stop_words"]
    word_similarity = models_json["word_similarity"]
    topic_model = models_json["topic_model"]
    
    # Kết quả trả về có dạng
    result = {
        "summary_document": "",  # văn bản sau khi tóm tắt
    }
    
    # Thực hiện tóm tắt một cụm văn bản
    print("Sumarizing..............................")
    summary_document, _, _ = (
        inference.summary_cluster_document(
            document_list, topic_model, word_similarity, options, list_stop_word
        )
    )
    sorted_summary_document = sorted(summary_document, key=lambda x: x.position)
    # Kết quả tóm tắt của toàn bộ văn bản
    summary_document_str = inference.concat_list_summary_sentences(
        sorted_summary_document, with_position=False
    ).replace("\n","")

    # Kết quả trả về
    result["summary_document"] = summary_document_str

    return JSONResponse(result)