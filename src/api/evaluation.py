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

def return_evaluation_for_GUI(evaluate: list[dict]):
    '''
    evaluate có dạng
    [{'ROUGE-1':[value], 'ROUGE-2':[value], "ROUGE_L":[value], "BertScore":[value]},
    {'ROUGE-1':[value], 'ROUGE-2':[value], "ROUGE_L":[value], "BertScore":[value]}]
    
    Độ dài của evaluate tuỳ thuộc vào số cách tóm tắt được đưa vào
    '''
    evaluate_metric = ["ROUGE-1", "ROUGE-2", "ROUGE-L", "BertScore"]
    return_evaluation = []
    for evaluate_instance in evaluate:
        evaluation = {} 
        for metric in evaluate_metric:
            max_value = max(evaluate_instance[f"{metric}"])
            min_value = min(evaluate_instance[f"{metric}"])
            mean_value = mean(evaluate_instance[f"{metric}"])
            evaluation[f"{metric}"] = [max_value, min_value, mean_value]
        return_evaluation.append(evaluation)

    return return_evaluation
