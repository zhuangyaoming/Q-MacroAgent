from llm.deepseek_llm import DeepSeekLLM
from tools.data_loader import load_data
from tools.graph_utils import build_industry_graph, analyze_key_factors, visualize_industry_graph, visualize_industry_graph_graphviz

class IndustryAgent:
    def __init__(self):
        self.llm = DeepSeekLLM()

    def analyze(self, data_path):
        factors, path_weights, time_series, df = load_data(data_path)
        G = build_industry_graph(factors, path_weights, df)
        key_factors = analyze_key_factors(G, time_series)
        # 可视化
        graph_img_path = "industry_graph.png"
        # visualize_industry_graph(G, save_path=graph_img_path)
        visualize_industry_graph_graphviz(G, save_path=graph_img_path)
        prompt = self._generate_prompt(key_factors, time_series)
        report = self.llm.chat(prompt)
        return report, graph_img_path

    def _generate_prompt(self, key_factors, time_series):
        # 组织成 LLM 能理解的 prompt
        prompt = f"请根据以下关键因子和时间序列数据，分析行业趋势并预测未来走向：\n关键因子：{key_factors}\n时间序列数据：{time_series}"
        return prompt 