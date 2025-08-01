import os
from tools.regional_loader import RegionalReportLoader
from tools.regional_graph_utils import (
    build_region_graph, analyze_region_clusters, find_hub_companies, calculate_synergy_score, visualize_region_graph, save_region_txt_report
)
from llm.deepseek_llm import DeepSeekLLM

class RegionalAgent:
    def __init__(self):
        self.loader = RegionalReportLoader()
        self.llm = DeepSeekLLM()  # 新增

    def analyze_region(self, company_reports_dir, region_name, output_path=None, similarity_threshold=0.7,
                      min_weight=0.85, top_n_hubs=None, max_edges_per_node=3):
        """
        分析指定地区，自动生成地区分析报告
        """
        # 1. 加载公司报告
        company_reports = self.loader.load_company_reports(company_reports_dir, region_name)
        if not company_reports:
            print(f"未找到地区 {region_name} 的公司报告")
            return None

        # 2. 提取公司名、量子特征、行业
        companies = []
        quantum_features = {}
        industry_map = {}
        for item in company_reports:
            report = item['report']
            name = report.get('company_name', '未知公司')
            companies.append(name)
            # 量子特征
            qf = None
            if 'analysis_metadata' in report:
                qf = report['analysis_metadata'].get('quantum_metadata', {}).get('quantum_features', None)
                industry = report['analysis_metadata'].get('company_basic_info', {}).get('industry', '未知行业')
            else:
                industry = '未知行业'
            if qf is not None:
                quantum_features[name] = qf
            else:
                quantum_features[name] = [0, 0, 0, 0]  # 占位
            industry_map[name] = industry

        # 3. 构建企业网络图
        G = build_region_graph(companies, quantum_features, industry_map, similarity_threshold=similarity_threshold)

        # 4. 图分析
        clusters = analyze_region_clusters(G)
        hubs = find_hub_companies(G, top_n=3)
        synergy_score = calculate_synergy_score(G)
        graph_img_path = visualize_region_graph(
            G,
            save_path=f"region_{region_name.replace('，','_')}_graph.png",
            min_weight=min_weight,
            top_n_hubs=top_n_hubs,
            max_edges_per_node=max_edges_per_node
        )

        # 5. 汇总并生成结构化报告
        regional_report = self.loader.generate_regional_report(company_reports, region_name)
        regional_report['network_analysis'] = {
            'clusters': [list(cluster) for cluster in clusters],
            'hub_companies': hubs,
            'synergy_score': synergy_score,
            'graph_image': graph_img_path
        }

        # 新增：生成prompt并调用LLM
        prompt = self._generate_region_prompt(regional_report)
        llm_report = self.llm.chat(prompt)
        regional_report['llm_report'] = llm_report

        # 6. 保存报告
        if output_path is None:
            output_path = f"regional_report_{region_name.replace('，','_')}.json"
        self.loader.save_regional_report(regional_report, output_path)
        print(f"地区分析报告已保存至: {output_path}")

        # 7. 生成txt文本报告
        txt_path = os.path.splitext(output_path)[0] + ".txt"
        save_region_txt_report(regional_report, txt_path)

        return regional_report

    def _generate_region_prompt(self, regional_report):
        # 组织prompt内容
        return f"""请根据以下地区企业网络分析数据，生成一份面向投资者的地区产业集群与创新协同分析报告：
        地区名称：{regional_report['region_name']}
        公司数量：{regional_report['companies_count']}
        产业分布：{regional_report['industry_distribution']}
        产业集群强度：{regional_report['regional_insights']['economic_cluster_strength']}
        创新潜力：{regional_report['regional_insights']['innovation_potential']}
        协同分数：{regional_report['network_analysis']['synergy_score']}
        枢纽企业：{regional_report['network_analysis']['hub_companies']}
        投资建议：{regional_report['investment_recommendations']}
        """ 