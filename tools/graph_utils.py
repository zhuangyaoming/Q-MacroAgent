import networkx as nx
import ast
import matplotlib.pyplot as plt

# def build_industry_graph(factors, path_weights):
#     G = nx.DiGraph()
#     # 示例：添加节点和边，实际需根据数据结构调整
#     if factors is not None:
#         for idx, factor in enumerate(factors):
#             G.add_node(idx, factor=factor)
#     if path_weights is not None:
#         for idx, weight in enumerate(path_weights):
#             # 假设path_weights为[(src, dst, weight), ...]
#             if isinstance(weight, (list, tuple)) and len(weight) == 3:
#                 G.add_edge(weight[0], weight[1], weight=weight[2])
#     return 
from collections import defaultdict

def build_industry_graph(factors, path_weights, df):
    G = nx.DiGraph()  # 必须是有向图
    companies = df['company'].unique()
    for company in companies:
        G.add_node(company)
    edge_weights = defaultdict(list)
    for idx, row in df.iterrows():
        src = row['company']
        pw_str = row['path_weights']
        pw_list = [x for x in pw_str.strip('[]').split(';') if x]
        for edge in pw_list:
            edge = edge.strip('() ')
            parts = edge.split(',')
            if len(parts) == 3:
                _, dst, weight = parts
                weight = float(weight.strip(' )]}\n\r\t'))
                edge_weights[(src, dst)].append(weight)
    # 只对 (src, dst) 加边，不会覆盖 (dst, src)
    for (src, dst), weights in edge_weights.items():
        avg_weight = sum(weights) / len(weights)
        G.add_edge(src, dst, weight=avg_weight)
    return G

def analyze_key_factors(G, time_series_data):
    # 示例：返回节点度数最高的因子，实际可扩展为更复杂的图分析
    if G.number_of_nodes() == 0:
        return []
    degrees = G.degree()
    sorted_nodes = sorted(degrees, key=lambda x: x[1], reverse=True)
    key_factors = [G.nodes[n]['factor'] for n, _ in sorted_nodes[:3] if 'factor' in G.nodes[n]]
    return key_factors


def visualize_industry_graph(G, save_path="industry_graph.png"):
    import matplotlib.pyplot as plt
    import networkx as nx
    import numpy as np

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1200)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    nx.draw_networkx_edges(
        G, pos, arrowstyle='-|>', arrowsize=30, edge_color='gray',
        width=2, connectionstyle='arc3,rad=0.2'
    )

    # 显示每条边的权重
    edge_label_count = 0
    for (src, dst, data) in G.edges(data=True):
        # 获取起点、终点坐标
        x1, y1 = pos[src]
        x2, y2 = pos[dst]

        # 计算边的方向向量
        dx, dy = x2 - x1, y2 - y1

        # 计算标签位置：用不同的偏移控制避免重叠
        if G.has_edge(dst, src) and src != dst:
            if (src, dst) < (dst, src):
                offset_ratio = 0.3
                offset_sign = 1
            else:
                offset_ratio = 0.3
                offset_sign = -1
        else:
            offset_ratio = 0.5
            offset_sign = 0

        # 标签放置在边的某一比例点上，并添加垂直偏移
        xm = x1 + dx * offset_ratio
        ym = y1 + dy * offset_ratio

        # 添加垂直于边方向的偏移（正交向量）
        norm = np.sqrt(dx ** 2 + dy ** 2)
        if norm == 0:
            norm = 1
        nx_, ny_ = -dy / norm, dx / norm  # 正交向量
        xm += offset_sign * 0.1 * nx_
        ym += offset_sign * 0.1 * ny_

        # 显示权重标签
        plt.text(
            xm, ym, f"{data['weight']:.2f}",
            color='red', fontsize=10, ha='center', va='center',
            bbox=dict(facecolor='white', edgecolor='none', pad=0.5)
        )
        edge_label_count += 1

    print(f"实际标注了 {edge_label_count} 条边的权值")
    plt.title("行业企业关系有向图")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path

from graphviz import Digraph
import os

def visualize_industry_graph_graphviz(G, save_path="industry_graph", fmt="png"):
    """
    使用 graphviz 绘制有向图，包括双向边和边的权值。
    :param G: networkx.DiGraph
    :param save_path: 可带或不带扩展名
    :param fmt: 输出格式，如 png、pdf、svg 等
    """
    # 去除扩展名，防止重复
    save_path = os.path.splitext(save_path)[0]
    dot = Digraph(format=fmt)
    dot.attr(rankdir='LR')  # 从左到右布局，也可以改为 TB（上下）

    # 添加节点
    for node in G.nodes():
        dot.node(str(node), shape='ellipse', style='filled', fillcolor='lightblue')

    # 添加边（权值作为标签）
    for u, v, data in G.edges(data=True):
        label = f"{data.get('weight', 1.0):.2f}"
        dot.edge(str(u), str(v), label=label)

    # 渲染图像（输出文件路径 = save_path + .fmt）
    filepath = dot.render(filename=save_path, cleanup=True)
    # 确保返回的路径带有正确的后缀
    if not filepath.endswith(f".{fmt}"):
        filepath = f"{filepath}.{fmt}"
    print(f"图已保存至: {filepath}")
    return filepath
