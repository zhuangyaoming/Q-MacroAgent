import networkx as nx
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
import os

def set_chinese_font():
    """
    自动设置matplotlib中文字体，优先使用SimHei、微软雅黑等。
    """
    font_candidates = [
        'SimHei', 'Microsoft YaHei', 'STSong', 'Arial Unicode MS', 'Heiti SC', 'PingFang SC'
    ]
    found = False
    for font in font_candidates:
        try:
            plt.rcParams['font.sans-serif'] = [font]
            plt.rcParams['axes.unicode_minus'] = False
            # 测试字体
            fig, ax = plt.subplots()
            ax.set_title('测试中文', fontsize=10)
            fig.canvas.draw()
            plt.close(fig)
            found = True
            break
        except Exception:
            continue
    if not found:
        print("警告：未检测到常用中文字体，中文可能无法正常显示。建议安装SimHei或微软雅黑字体。")

def build_region_graph(companies, quantum_features, industry_map, similarity_threshold=0.7):
    """
    构建地区企业关系图
    companies: 公司名列表
    quantum_features: {公司名: [特征向量]}
    industry_map: {公司名: 行业}
    similarity_threshold: 量子特征相似度阈值
    """
    G = nx.Graph()
    for company in companies:
        G.add_node(company, industry=industry_map.get(company, "未知"))
    # 以量子特征余弦相似度为边
    for i, c1 in enumerate(companies):
        for j, c2 in enumerate(companies):
            if i < j:
                v1, v2 = quantum_features[c1], quantum_features[c2]
                sim = cosine_similarity(v1, v2)
                if sim >= similarity_threshold:
                    G.add_edge(c1, c2, weight=sim)
    return G

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

def analyze_region_clusters(G):
    """
    识别产业集群（连通分量/社区）
    """
    clusters = list(nx.connected_components(G))
    return clusters

def find_hub_companies(G, top_n=3):
    """
    识别枢纽企业（度数最高/中心性最高）
    """
    degree_dict = dict(G.degree())
    sorted_hubs = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_hubs[:top_n]

def calculate_synergy_score(G):
    """
    计算地区企业协同效应（平均边权/网络密度等）
    """
    if G.number_of_edges() == 0:
        return 0
    weights = [d['weight'] for u, v, d in G.edges(data=True)]
    return np.mean(weights)

def visualize_region_graph(
    G, 
    save_path="region_graph.png", 
    min_weight=0.85, 
    top_n_hubs=None, 
    max_edges_per_node=None
):
    """
    可视化企业网络，只显示重要节点联系
    min_weight: 只显示权重大于该阈值的边
    top_n_hubs: 只显示枢纽节点及其边（可选）
    max_edges_per_node: 每个节点最多显示K条最强联系（可选）
    """
    set_chinese_font()
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)

    # 过滤边
    edges_to_draw = []
    if min_weight is not None:
        edges_to_draw = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] >= min_weight]
    else:
        edges_to_draw = list(G.edges())

    # 只保留枢纽节点及其边
    if top_n_hubs is not None:
        degree_dict = dict(G.degree())
        hubs = sorted(degree_dict, key=degree_dict.get, reverse=True)[:top_n_hubs]
        edges_to_draw = [(u, v) for u, v in edges_to_draw if u in hubs or v in hubs]

    # 限制每个节点最多显示K条最强联系
    if max_edges_per_node is not None:
        filtered_edges = set()
        for node in G.nodes():
            neighbors = sorted(
                [(v, G[node][v]['weight']) for v in G.neighbors(node) if (node, v) in edges_to_draw or (v, node) in edges_to_draw],
                key=lambda x: x[1], reverse=True
            )
            for v, _ in neighbors[:max_edges_per_node]:
                if (node, v) in G.edges():
                    filtered_edges.add((node, v))
                elif (v, node) in G.edges():
                    filtered_edges.add((v, node))
        edges_to_draw = list(filtered_edges)

    nx.draw_networkx_nodes(G, pos, node_color='skyblue')
    nx.draw_networkx_labels(G, pos, font_size=10)
    nx.draw_networkx_edges(G, pos, edgelist=edges_to_draw, edge_color='gray')
    plt.title("地区企业关系网络（精简版）")
    plt.savefig(save_path)
    plt.close()
    return save_path

def save_region_txt_report(region_report, output_path):
    """
    生成地区分析txt报告
    region_report: 地区分析报告dict
    output_path: txt文件路径
    """
    lines = []
    lines.append(f"地区名称：{region_report.get('region_name', '')}")
    lines.append(f"分析时间：{region_report.get('analysis_timestamp', '')}")
    lines.append(f"公司数量：{region_report.get('companies_count', 0)}")
    lines.append(f"产业分布：{region_report.get('industry_distribution', {})}")
    
    # 产业集群强度
    cluster = region_report.get('regional_insights', {}).get('economic_cluster_strength', {})
    lines.append(f"产业集群强度：{cluster.get('strength_level', '未知')}（多样性得分：{cluster.get('diversity_score', '无')}）")
    lines.append(f"集群建议：{cluster.get('recommendation', '')}")
    
    # 创新潜力
    innovation = region_report.get('regional_insights', {}).get('innovation_potential', {})
    lines.append(f"创新潜力：{innovation.get('potential_level', '未知')}（创新分数：{innovation.get('innovation_score', '无')}）")
    
    # 协同分数
    synergy = region_report.get('network_analysis', {}).get('synergy_score', '无')
    lines.append(f"企业协同分数：{synergy}")
    
    # 枢纽企业
    hubs = region_report.get('network_analysis', {}).get('hub_companies', [])
    lines.append(f"枢纽企业（度数最高）：")
    for hub in hubs:
        lines.append(f"  - {hub[0]}（度数：{hub[1]}）")
    
    # 投资建议
    invest = region_report.get('investment_recommendations', {})
    lines.append(f"投资建议：{invest.get('recommendation_level', '未知')}，策略：{invest.get('investment_strategy', '')}")
    
    # 风险评估
    risk = region_report.get('risk_assessment', {})
    lines.append(f"风险等级：{risk.get('risk_level', '未知')}，主要风险：{risk.get('risk_factors', [])}")
    if 'mitigation_suggestions' in risk:
        lines.append(f"风险缓解建议：{risk['mitigation_suggestions']}")
    
    # 主要增长驱动
    growth = region_report.get('regional_insights', {}).get('growth_drivers', [])
    lines.append(f"主要增长驱动：{growth}")
    
    # 主要公司列表
    lines.append("公司列表：")
    for c in region_report.get('companies', []):
        lines.append(f"  - {c.get('name', '')}（行业：{c.get('industry', '未知')}）")
    
    # LLM生成的智能分析报告
    if 'llm_report' in region_report:
        lines.append("\n" + "="*50)
        lines.append("AI智能分析报告")
        lines.append("="*50)
        lines.append(region_report['llm_report'])
    
    # 结尾
    lines.append("\n（本报告由智能分析系统自动生成，仅供参考）")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"地区分析txt报告已保存至: {output_path}") 