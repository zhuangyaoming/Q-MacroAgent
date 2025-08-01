#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试地区报告整合工具
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.regional_loader import RegionalReportLoader

def test_regional_loader():
    """测试地区报告整合工具"""
    
    # 初始化工具
    loader = RegionalReportLoader()
    
    # 设置数据目录
    data_directory = "data/json研报"
    #"data/地区分析data/company_reports"
    
    print("=== 地区报告整合工具测试 ===")
    
    # 测试1: 加载所有公司报告
    print("\n1. 加载公司报告...")
    company_reports = loader.load_company_reports(data_directory)
    print(f"   找到 {len(company_reports)} 个公司报告")
    
    # 显示各地区分布
    region_groups = loader.group_by_region(company_reports)
    print(f"   地区分布: {list(region_groups.keys())}")
    
    # 测试2: 处理特定地区
    print("\n2. 处理特定地区...")
    
    # 尝试处理"中国，北京市"地区
    beijing_reports = loader.load_company_reports(data_directory, "中国，北京市")
    if beijing_reports:
        print(f"   找到 {len(beijing_reports)} 个北京市的公司报告")
        
        # 生成地区报告
        regional_report = loader.generate_regional_report(beijing_reports, "中国，北京市")
        
        print(f"   地区报告生成完成，包含 {regional_report.get('companies_count', 0)} 家公司")
        print(f"   产业集群强度: {regional_report.get('regional_insights', {}).get('economic_cluster_strength', {}).get('strength_level', '未知')}")
        print(f"   创新潜力: {regional_report.get('regional_insights', {}).get('innovation_potential', {}).get('potential_level', '未知')}")
        print(f"   投资建议: {regional_report.get('investment_recommendations', {}).get('recommendation_level', '未知')}")
        
        # 保存报告
        output_path = "beijing_regional_report.json"
        loader.save_regional_report(regional_report, output_path)
        print(f"   地区报告已保存至: {output_path}")
        
    else:
        print("   未找到北京市的公司报告")
    
    # 测试3: 处理其他地区
    print("\n3. 处理其他地区...")
    
    # 查找所有地区
    all_regions = list(region_groups.keys())
    print(f"   发现地区: {all_regions}")
    
    for region in all_regions[:3]:  # 只处理前3个地区
        print(f"\n   处理地区: {region}")
        region_reports = region_groups[region]
        
        if len(region_reports) >= 2:  # 至少2家公司才生成报告
            regional_report = loader.generate_regional_report(region_reports, region)
            
            companies_count = regional_report.get('companies_count', 0)
            cluster_strength = regional_report.get('regional_insights', {}).get('economic_cluster_strength', {}).get('strength_level', '未知')
            
            print(f"     包含 {companies_count} 家公司")
            print(f"     产业集群强度: {cluster_strength}")
            
            # 保存报告
            safe_region_name = region.replace('，', '_').replace(' ', '_')
            output_path = f"{safe_region_name}_regional_report.json"
            loader.save_regional_report(regional_report, output_path)
        else:
            print(f"     公司数量不足，跳过生成报告")

if __name__ == "__main__":
    test_regional_loader() 