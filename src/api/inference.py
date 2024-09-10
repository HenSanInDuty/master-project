from typing import Tuple
from .genetic_algorithm import GAS
from .utils import get_noun_word, pos_tag_document
from . import models
from itertools import chain


def count_all_terminology(
    sentences: list[models.Sentence],
    topic_model: dict,
    topic: str | None,
    stop_words: list[str],
    option_trainning: models.OptionTrainning,
) -> dict:
    """
    Đếm số lần xuất hiện của các thuật ngữ và trả về dict

    Param
    -----------------------------------------
    sentences: văn bản đã được đánh dấu từ loại
    topic: chủ đề của văn bản (nếu không biết trước thì đặt là None)

    Return
    -----------------------------------------
    dict: chứa số lần xuất hiện của tất cả thuật ngữ
    {terminology: count, all: count}
    """

    terminologys = {}

    words = [sentence.content.split(" ") for sentence in sentences]

    # Flatten list từ
    words = list(chain.from_iterable(words))

    # Lấy ra những danh từ
    noun_words = get_noun_word(words, option_trainning.pos_tool, stop_words)

    # Đếm các thuật ngữ có trong văn bản
    model_terminologys = [word[0] for word in topic_model[f"{topic}"]]
    count_all = 0
    for noun in noun_words:
        if noun in model_terminologys:
            count_all += 1
            if noun in terminologys.keys():
                terminologys[f"{noun}"] += 1
            else:
                terminologys[f"{noun}"] = 1

    terminologys["terminologies_count_all"] = count_all
    return terminologys


def weight_terminology(
    sentences: str,
    terminology_count: dict,
    stop_words: list[str],
    option_trainning: models.OptionTrainning,
) -> float:
    """
    Tính trọng số của các thuật ngữ trong một câu

    Param
    ---------------------------------------------
    sentences: câu cần tính trọng số
    terminology_count: tập các thuật ngữ
    stop_words: danh sách hư từ

    Return
    --------------------------------------------
    Trọng số: float
    """

    words = sentences.split(" ")
    noun_word = get_noun_word(words, option_trainning.pos_tool, stop_words)

    # Trọng số của câu
    weight = 0

    # Lấy ra các thuật ngữ trong câu
    noun_word = [noun for noun in noun_word if noun in terminology_count.keys()]

    # Không có thuật ngữ nào trong câu
    if len(noun_word) == 0:
        return 0

    # Tính trọng số cho từng thuật ngữ
    noun_word.sort()
    noun_weight = 1
    noun_current = noun_word[0]
    for i in range(1, len(noun_word)):
        if noun_word[i] != noun_current:
            # Số lần xuất hiện của thuật ngữ chia cho toàn bộ số lần xuất hiện của các thuật ngữ khác
            weight += noun_weight / terminology_count["terminologies_count_all"]
            noun_current = noun_word[i]
            noun_weight = 1
        else:
            noun_weight += 1
    weight += noun_weight / terminology_count["terminologies_count_all"]
    return weight


def cal_sentences_weight(
    sentences: list[models.Sentence],
    terminology_count: dict,
    stop_words: list[str],
    option_trainning: models.OptionTrainning,
) -> list:
    """
    Tính trọng số của các câu trong văn bản

    Params
    ----------------------------
    terminology_word: thuật ngữ trong câu
    terminology_count: các thuật ngữ có trong văn bản

    Return
    -----------------------------
    Trả về list có định dạng như sau:
    [
        {
            id: id của câu,
            content: nội dung câu,
            weight: trọng số của câu dựa vào thuật ngữ
        }
    ]
    """

    sentences_evaluate = [sentence.content for sentence in sentences]
    weighted_sentences = []
    total_weight = 0
    for i in range(len(sentences_evaluate)):
        weight = weight_terminology(
            sentences_evaluate[i], terminology_count, stop_words, option_trainning
        )
        total_weight += weight
        weighted_sentences.append(
            {"id": f"S{i+1}", "content": sentences_evaluate[i], "weight": weight}
        )
    weighted_sentences.append(total_weight)
    return weighted_sentences


def concat_list_summary_sentences(
    summary_sentences: list[models.Sentence], with_position: bool = False
) -> str:
    """
    Cộng chuỗi các câu để tóm tắt

    Param
    -------------------------------
    summary_sentences: danh sách các câu

    Return
    -------------------------------
    str: Văn bảng tóm tắt theo thứ tự
    """

    summary_sentences = [
        [sentence.position, sentence.content_original] for sentence in summary_sentences
    ]
    summary_document = ""
    summary_sentences = sorted(summary_sentences, key=lambda x: x[0])

    for summary_sentence in summary_sentences:
        summary_document += summary_sentence[1] + "."
        if with_position:
            summary_document += str(summary_sentence[0])

    return summary_document


def search_topic_document(
    document: models.Document,
    topic_models: dict,
    stop_words: list[str],
    option_trainning: models.OptionTrainning,
):

    topic_avaiable = topic_models.keys()
    topic_needed = ""
    max_weight = 0

    for topic in topic_avaiable:
        # Đếm các thuật ngữ
        terminologies = count_all_terminology(
            document.sentences, topic_models, topic, stop_words, option_trainning
        )

        # Tính trọng số của câu
        sentences_weights = cal_sentences_weight(
            document.sentences, terminologies, stop_words, option_trainning
        )

        if sentences_weights[len(sentences_weights) - 1] > max_weight:
            max_weight = sentences_weights[len(sentences_weights) - 1]
            topic_needed = topic

    return topic_needed


def calculate_similarity_sentence(
    sen1: models.Sentence,
    sen2: models.Sentence,
    word_similarity: dict,
    option_trainning: models.OptionTrainning,
    stop_words: list[str],
):
    """ """

    match word_similarity["type"]:
        case "PMI":
            similarity = 0
            words_sen1 = get_noun_word(
                sen1.content.split(" "), option_trainning.pos_tool, stop_words
            )
            words_sen2 = get_noun_word(
                sen2.content.split(" "), option_trainning.pos_tool, stop_words
            )
            words_sen1.sort()
            words_sen2.sort()
            for word1 in words_sen1:
                for word2 in words_sen2:
                    word_pair = word1 + " " + word2
                    if word_pair in word_similarity["word_similarity"].keys():
                        similarity += word_similarity["word_similarity"][f"{word_pair}"]
            return similarity
        case _:
            raise Exception(f"Chưa hỗ trợ độ tương đồng {word_similarity['type']}")


def calculate_similarity_document(
    doc1: models.Document, doc2: models.Document, sentences_similarity: dict
):
    """ """
    similarity = 0
    for sentence_doc1 in doc1.sentences:
        for sentence_doc2 in doc2.sentences:
            key = f"{sentence_doc1.position} {sentence_doc2.position}"
            if key in sentences_similarity.keys():
                similarity += sentences_similarity[f"{key}"]
    return similarity / (len(doc1.sentences) * len(doc2.sentences))


def summary_cluster_document(
    documents: list[dict],
    topic_models: dict,
    word_similarity: dict,
    option_trainning: models.OptionTrainning,
    stop_words: list[str],
) -> Tuple[list[models.Sentence], dict]:
    """ """

    # 0. Đánh dấu vị trí của từng câu, từng câu sẽ có vị trí trong toàn bộ văn bản và vị trí trong từng văn bản cụ thế
    cluster_document_len = 0
    documents_with_position: list[models.Document] = []
    sentences_in_cluster_document: list[models.Sentence] = []
    i = 0
    j = 0
    for document in documents:
        # Tính độ dài của cụm văn bản cho việc tóm tắt ở bước 6
        cluster_document_len += len(document["content"])
        document_instance = models.Document([], document["topic"], j)
        tagged_document = pos_tag_document(
            document["content"], option_trainning.pos_tool
        )
        sentences = tagged_document.split("./.")
        for sentence in sentences:
            sentence_with_position = models.Sentence(sentence, i, "")
            sentence_with_position.set_document_position(j)
            document_instance.add_sentence(sentence_with_position)
            sentences_in_cluster_document.append(sentence_with_position)
            i += 1
        documents_with_position.append(document_instance)
        j += 1

    # 1. Xác định các chủ đề cho các văn bản
    topic_avaiable = topic_models.keys()
    for i in range(len(documents_with_position)):
        if documents_with_position[i].topic not in topic_avaiable:
            documents_with_position[i].set_topic(
                search_topic_document(
                    documents_with_position[i],
                    topic_models,
                    stop_words,
                    option_trainning,
                )
            )

    # 2. Tính trọng số cho từng câu trong văn bản và trọng số của từng văn bản trong cụm văn bản
    # Tính toán trọng số cho các văn bản
    min_weight_document = 0
    max_weight_document = 0

    for i in range(len(documents_with_position)):
        # Đếm các thuật ngữ
        terminologies = count_all_terminology(
            documents_with_position[i].sentences,
            topic_models,
            documents_with_position[i].topic,
            stop_words,
            option_trainning,
        )

        # Tính trọng số của câu
        sentences_weights = cal_sentences_weight(
            documents_with_position[i].sentences,
            terminologies,
            stop_words,
            option_trainning,
        )

        documents_with_position[i].apply_weight_for_sentences(sentences_weights)

        if min_weight_document > documents_with_position[i].weight:
            min_weight_document = documents_with_position[i].weight

        if max_weight_document < documents_with_position[i].weight:
            max_weight_document = documents_with_position[i].weight

    # Chuẩn hoá lại trọng số của cụm văn bản
    for i in range(len(documents_with_position)):
        if min_weight_document != max_weight_document:
            documents_with_position[i].set_weight(
                (documents_with_position[i].weight - min_weight_document)
                / (max_weight_document - min_weight_document)
            )
        else:
            documents_with_position[i].set_weight(1)

    # Cập nhật lại trọng số cho từng câu
    for i in range(len(documents_with_position)):
        documents_with_position[i].apply_document_weight_for_sentences()

    # 3. Tính toán độ tương đồng cho các câu không phân biệt chủ đề
    sentence_similarity = {}
    for i in range(len(sentences_in_cluster_document) - 1):
        for j in range(i + 1, len(sentences_in_cluster_document)):
            key = f"{sentences_in_cluster_document[i].position} {sentences_in_cluster_document[j].position}"
            similarity = calculate_similarity_sentence(
                sentences_in_cluster_document[i],
                sentences_in_cluster_document[j],
                word_similarity,
                option_trainning,
                stop_words,
            )
            sentence_similarity[f"{key}"] = similarity

    # 4. Tính toán độ tương đồng giữa các văn bản
    document_similarity = {}
    for i in range(len(documents_with_position) - 1):
        for j in range(i + 1, len(documents_with_position)):
            key = f"{i} {j}"
            similarity = calculate_similarity_document(
                documents_with_position[i],
                documents_with_position[j],
                sentence_similarity,
            )
            document_similarity[f"{key}"] = similarity

    # 5. Cập nhật lại độ tương đồng cho từng cặp câu
    for i in range(len(sentences_in_cluster_document) - 1):
        for j in range(i + 1, len(sentences_in_cluster_document)):
            sentence_key = f"{i} {j}"
            if (
                sentences_in_cluster_document[i].document_position
                != sentences_in_cluster_document[j].document_position
            ):
                document_key = f"{sentences_in_cluster_document[i].document_position} {sentences_in_cluster_document[j].document_position}"
                sentence_similarity[f"{key}"] = (
                    sentence_similarity[f"{sentence_key}"]
                    + document_similarity[f"{document_key}"]
                )

    # 6. Chọn lọc các câu có trọng số câu nhất và có tổng độ tương đồng thấp nhất theo phương pháp GA
    optimizer = GAS(
        sentences_in_cluster_document,
        sentence_similarity,
        option_trainning.r_threshold * cluster_document_len,
    )
    best_solution, best_fitness = optimizer.fit()

    # 9. Trả về tập các câu được chọn
    final_summary = []
    for index in best_solution:
        final_summary.append(sentences_in_cluster_document[index])
    return final_summary, sentence_similarity, sentences_in_cluster_document
