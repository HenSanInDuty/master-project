from rouge import Rouge
from bert_score import BERTScorer
from statistics import mean


def ROUGE_evaluate(document: str, summary_document: str):
    rouge = Rouge()
    score = rouge.get_scores(summary_document, document)
    return score[0]


def BertScore_evaluate(document: str, summary_document: str):
    scorer = BERTScorer(lang="vi")
    _, _, F1_1 = scorer.score([document], [summary_document])
    return F1_1.tolist()[0]


# def Gemini_evaluate(document:str, summary_document:str):


def return_evaluation_for_GUI(evalute: dict):
    evaluate_metric = ["ROUGE-1", "ROUGE-2", "ROUGE-L", "BertScore"]
    return_evaluation = {}
    for metric in evaluate_metric:
        max_value = max(evalute[f"{metric}"])
        min_value = min(evalute[f"{metric}"])
        mean_value = mean(evalute[f"{metric}"])
        return_evaluation[f"{metric}"] = [max_value, min_value, mean_value]

    return return_evaluation
