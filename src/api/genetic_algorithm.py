import random
from . import models
from deap import base, creator, tools, algorithms

class GAS():
    num_nodes: int
    toolbox: base.Toolbox
    sentences: list[models.Sentence]
    sentences_similarity: dict
    max_total_length: float
    
    def __init__(self, 
                sentences:list[models.Sentence],
                sentences_similarity: dict,
                max_total_length:float):
        #
        self.sentences = sentences
        self.sentences_similarity = sentences_similarity
        
        # Số đỉnh và tổng giá trị độ dài giới hạn
        self.max_total_length = max_total_length

        # Tạo lớp Fitness và Individual
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # Khởi tạo quần thể
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_item", lambda: random.choice([0, 1]))  # Chọn ngẫu nhiên 0 hoặc 1 cho mỗi đỉnh
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_item, len(self.sentences))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

    # Hàm tính fitness
    def evaluate(self, individual, alpha=1, beta=1, penalty=1000):
        # Chọn các đỉnh dựa trên cá thể
        selected_sentences = [i for i, bit in enumerate(individual) if bit == 1]
        
        # Tính tổng độ dài của các câu được chọn
        total_node_length = sum(len(self.sentences[i].content) for i in selected_sentences)
        
        # Kiểm tra ràng buộc: tổng độ dài không vượt quá max_total_length
        if total_node_length > self.max_total_length:
            return -penalty,  # Trả về giá trị âm lớn để phạt cá thể vi phạm

        # Tính tổng trọng số của các câu được chọn
        total_weight = sum(self.sentences[i].weight for i in selected_sentences)
        
        # Tính tổng độ tương đồng của các câu được chọn
        total_similarity = 0
        for i in range(len(selected_sentences) - 1):
            for j in range(i + 1, len(selected_sentences)):
                key = f'{selected_sentences[i]} {selected_sentences[j]}'
                if selected_sentences[j] < selected_sentences[i]:
                    key = f'{selected_sentences[j]} {selected_sentences[i]}'
                    
                total_similarity += self.sentences_similarity[f'{key}']
                
        # Tính giá trị fitness
        fitness_value = alpha * total_weight - beta * total_similarity
        return fitness_value,

    # Hàm chạy giải thuật di truyền
    def fit(self):
        # Đăng ký các hàm cho giải thuật di truyền
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", self.evaluate)
        
        population = self.toolbox.population(n=100)
        
        # Chạy thuật toán tiến hóa
        algorithms.eaSimple(population, self.toolbox, cxpb=0.7, mutpb=0.2, ngen=50, verbose=True)
        
        # Chọn giải pháp tốt nhất
        best_individual = tools.selBest(population, k=1)[0]
        selected_nodes = [i for i, bit in enumerate(best_individual) if bit == 1]
        best_fitness = self.evaluate(best_individual)
        
        return selected_nodes, best_fitness
