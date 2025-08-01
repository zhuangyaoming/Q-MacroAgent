#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试地区分析代理
"""

from agent.regional_agent import RegionalAgent

def test_regional_agent():
    agent = RegionalAgent()
    # 设置公司报告目录和地区名
    company_reports_dir = "data/json研报"
    region_name = "中国，北京市"
    print(f"分析地区：{region_name}")
    report = agent.analyze_region(company_reports_dir, region_name)
    if report:
        print("\n=== 地区分析报告主要内容 ===")
        print(f"地区名称: {report.get('region_name')}")
        print(f"公司数量: {report.get('companies_count')}")
        print(f"产业分布: {report.get('industry_distribution')}")
        print(f"产业集群强度: {report.get('regional_insights', {}).get('economic_cluster_strength', {}).get('strength_level', '未知')}")
        print(f"创新潜力: {report.get('regional_insights', {}).get('innovation_potential', {}).get('potential_level', '未知')}")
        print(f"协同分数: {report.get('network_analysis', {}).get('synergy_score', '无')}")
        print(f"枢纽企业: {report.get('network_analysis', {}).get('hub_companies', [])}")
        print(f"企业网络图: {report.get('network_analysis', {}).get('graph_image', '')}")
        print(f"投资建议: {report.get('investment_recommendations', {}).get('recommendation_level', '未知')}")
    else:
        print("未生成地区分析报告")

if __name__ == "__main__":
    test_regional_agent() 