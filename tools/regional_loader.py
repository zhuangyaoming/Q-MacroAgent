import json
import os
import pandas as pd
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import re
from datetime import datetime

class RegionalReportLoader:
    """地区报告整合工具"""
    
    def __init__(self):
        self.region_data = {}
        self.company_reports = []
        
    def load_company_reports(self, directory_path: str, target_region: str = None) -> List[Dict]:
        """
        加载指定目录下的公司报告
        
        Args:
            directory_path: 公司报告文件目录
            target_region: 目标地区（如"中国，北京市"），如果为None则自动识别
            
        Returns:
            公司报告列表
        """
        company_reports = []
        
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                file_path = os.path.join(directory_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        
                    # 提取地区信息
                    region = self._extract_region_from_report(report)
                    
                    # 如果指定了目标地区，只加载该地区的报告
                    if target_region and region != target_region:
                        continue
                        
                    company_reports.append({
                        'filename': filename,
                        'region': region,
                        'report': report
                    })
                    
                except Exception as e:
                    print(f"加载文件 {filename} 时出错: {e}")
                    
        return company_reports
    
    def _extract_region_from_report(self, report: Dict) -> str:
        """从报告中提取地区信息"""
        # 优先从analysis_metadata中提取
        if 'analysis_metadata' in report:
            basic_info = report['analysis_metadata'].get('company_basic_info', {})
            if 'hq_location' in basic_info:
                return basic_info['hq_location']
        
        # 从文件名中提取地区信息
        if 'company_name' in report:
            # 尝试从tavily_report中提取地区信息
            tavily_report = report.get('tavily_report', '')
            # 查找包含"中国，"或"United States"等地区标识的文本
            region_patterns = [
                r'中国，([^，\n]+)',
                r'United States',
                r'California',
                r'New York',
                r'Beijing',
                r'Shanghai',
                r'深圳',
                r'广州'
            ]
            
            for pattern in region_patterns:
                match = re.search(pattern, tavily_report)
                if match:
                    if pattern == r'中国，([^，\n]+)':
                        return f"中国，{match.group(1)}"
                    else:
                        return match.group(0)
        
        return "未知地区"
    
    def group_by_region(self, company_reports: List[Dict]) -> Dict[str, List[Dict]]:
        """按地区分组公司报告"""
        region_groups = defaultdict(list)
        
        for report in company_reports:
            region = report['region']
            region_groups[region].append(report)
            
        return dict(region_groups)
    
    def generate_regional_report(self, region_reports: List[Dict], region_name: str) -> Dict:
        """
        生成地区分析报告
        
        Args:
            region_reports: 该地区的公司报告列表
            region_name: 地区名称
            
        Returns:
            地区分析报告
        """
        if not region_reports:
            raise ValueError(f"没有找到地区 {region_name} 的公司报告")
        
        # 提取基础信息
        companies_info = []
        quantum_features = []
        industry_distribution = defaultdict(int)
        
        for report_data in region_reports:
            report = report_data['report']
            company_name = report.get('company_name', '未知公司')
            
            # 提取公司基础信息
            company_info = {
                'name': company_name,
                'filename': report_data['filename']
            }
            
            # 提取行业信息
            if 'analysis_metadata' in report:
                basic_info = report['analysis_metadata'].get('company_basic_info', {})
                company_info['industry'] = basic_info.get('industry', '未知行业')
                industry_distribution[basic_info.get('industry', '未知行业')] += 1
            
            companies_info.append(company_info)
            
            # 提取量子特征
            if 'analysis_metadata' in report:
                quantum_meta = report['analysis_metadata'].get('quantum_metadata', {})
                if 'quantum_features' in quantum_meta:
                    quantum_features.append({
                        'company': company_name,
                        'features': quantum_meta['quantum_features'],
                        'advantage_score': quantum_meta.get('quantum_advantage_score', 0),
                        'entanglement_strength': quantum_meta.get('entanglement_strength', 0),
                        'measurement_probability': quantum_meta.get('measurement_probability', 0)
                    })
        
        # 计算地区级统计指标
        regional_stats = self._calculate_regional_statistics(quantum_features)
        
        # 生成地区报告
        regional_report = {
            "region_name": region_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "companies_count": len(region_reports),
            "companies": companies_info,
            "industry_distribution": dict(industry_distribution),
            "regional_statistics": regional_stats,
            "quantum_analysis": self._generate_regional_quantum_analysis(quantum_features),
            "regional_insights": self._generate_regional_insights(region_reports, regional_stats),
            "risk_assessment": self._assess_regional_risks(quantum_features),
            "investment_recommendations": self._generate_regional_investment_recommendations(regional_stats)
        }
        
        return regional_report
    
    def _calculate_regional_statistics(self, quantum_features: List[Dict]) -> Dict:
        """计算地区级统计指标"""
        if not quantum_features:
            return {}
        
        # 计算各维度的平均值
        feature_dimensions = len(quantum_features[0]['features'])
        avg_features = [0] * feature_dimensions
        
        advantage_scores = []
        entanglement_strengths = []
        measurement_probabilities = []
        
        for qf in quantum_features:
            features = qf['features']
            for i, feature in enumerate(features):
                avg_features[i] += feature
            
            advantage_scores.append(qf['advantage_score'])
            entanglement_strengths.append(qf['entanglement_strength'])
            measurement_probabilities.append(qf['measurement_probability'])
        
        # 计算平均值
        company_count = len(quantum_features)
        avg_features = [f / company_count for f in avg_features]
        
        return {
            "avg_quantum_features": avg_features,
            "avg_advantage_score": sum(advantage_scores) / len(advantage_scores),
            "avg_entanglement_strength": sum(entanglement_strengths) / len(entanglement_strengths),
            "avg_measurement_probability": sum(measurement_probabilities) / len(measurement_probabilities),
            "max_advantage_score": max(advantage_scores),
            "min_advantage_score": min(advantage_scores),
            "regional_diversity_score": self._calculate_diversity_score(quantum_features)
        }
    
    def _calculate_diversity_score(self, quantum_features: List[Dict]) -> float:
        """计算地区多样性得分"""
        if len(quantum_features) < 2:
            return 0.0
        
        # 计算特征向量的标准差作为多样性指标
        feature_dimensions = len(quantum_features[0]['features'])
        feature_std = [0] * feature_dimensions
        
        for i in range(feature_dimensions):
            values = [qf['features'][i] for qf in quantum_features]
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            feature_std[i] = variance ** 0.5
        
        # 多样性得分 = 平均标准差 / 平均特征值
        avg_std = sum(feature_std) / len(feature_std)
        avg_features = [sum(qf['features'][i] for qf in quantum_features) / len(quantum_features) 
                       for i in range(feature_dimensions)]
        avg_feature = sum(avg_features) / len(avg_features)
        
        return avg_std / avg_feature if avg_feature > 0 else 0.0
    
    def _generate_regional_quantum_analysis(self, quantum_features: List[Dict]) -> Dict:
        """生成地区量子分析"""
        if not quantum_features:
            return {}
        
        # 分析地区量子特征
        analysis = {
            "quantum_cluster_analysis": {
                "cluster_count": min(3, len(quantum_features)),  # 最多3个集群
                "cluster_characteristics": self._analyze_quantum_clusters(quantum_features)
            },
            "regional_quantum_signature": {
                "dominant_features": self._identify_dominant_features(quantum_features),
                "quantum_synergy_score": self._calculate_quantum_synergy(quantum_features)
            }
        }
        
        return analysis
    
    def _analyze_quantum_clusters(self, quantum_features: List[Dict]) -> List[Dict]:
        """分析量子集群特征"""
        # 简化的集群分析
        clusters = []
        
        # 按优势得分分组
        advantage_scores = [qf['advantage_score'] for qf in quantum_features]
        avg_advantage = sum(advantage_scores) / len(advantage_scores)
        
        high_performers = [qf for qf in quantum_features if qf['advantage_score'] > avg_advantage]
        low_performers = [qf for qf in quantum_features if qf['advantage_score'] <= avg_advantage]
        
        if high_performers:
            clusters.append({
                "cluster_type": "高表现集群",
                "company_count": len(high_performers),
                "avg_advantage_score": sum(qf['advantage_score'] for qf in high_performers) / len(high_performers),
                "companies": [qf['company'] for qf in high_performers]
            })
        
        if low_performers:
            clusters.append({
                "cluster_type": "发展集群",
                "company_count": len(low_performers),
                "avg_advantage_score": sum(qf['advantage_score'] for qf in low_performers) / len(low_performers),
                "companies": [qf['company'] for qf in low_performers]
            })
        
        return clusters
    
    def _identify_dominant_features(self, quantum_features: List[Dict]) -> List[Dict]:
        """识别主导特征"""
        if not quantum_features:
            return []
        
        feature_dimensions = len(quantum_features[0]['features'])
        feature_sums = [0] * feature_dimensions
        
        for qf in quantum_features:
            for i, feature in enumerate(qf['features']):
                feature_sums[i] += feature
        
        # 找出最显著的特征维度
        max_feature = max(feature_sums)
        dominant_features = []
        
        for i, feature_sum in enumerate(feature_sums):
            if feature_sum > max_feature * 0.8:  # 80%阈值
                dominant_features.append({
                    "dimension": i + 1,
                    "total_value": feature_sum,
                    "avg_value": feature_sum / len(quantum_features),
                    "significance": "高" if feature_sum > max_feature * 0.9 else "中"
                })
        
        return sorted(dominant_features, key=lambda x: x['total_value'], reverse=True)
    
    def _calculate_quantum_synergy(self, quantum_features: List[Dict]) -> float:
        """计算量子协同效应"""
        if len(quantum_features) < 2:
            return 0.0
        
        # 计算企业间的量子协同效应
        synergy_scores = []
        
        for i in range(len(quantum_features)):
            for j in range(i + 1, len(quantum_features)):
                qf1, qf2 = quantum_features[i], quantum_features[j]
                
                # 计算特征向量的相似度
                features1 = qf1['features']
                features2 = qf2['features']
                
                # 余弦相似度
                dot_product = sum(f1 * f2 for f1, f2 in zip(features1, features2))
                norm1 = sum(f1 ** 2 for f1 in features1) ** 0.5
                norm2 = sum(f2 ** 2 for f2 in features2) ** 0.5
                
                if norm1 > 0 and norm2 > 0:
                    similarity = dot_product / (norm1 * norm2)
                    synergy_scores.append(similarity)
        
        return sum(synergy_scores) / len(synergy_scores) if synergy_scores else 0.0
    
    def _generate_regional_insights(self, region_reports: List[Dict], regional_stats: Dict) -> Dict:
        """生成地区洞察"""
        insights = {
            "economic_cluster_strength": self._assess_cluster_strength(regional_stats),
            "innovation_potential": self._assess_innovation_potential(regional_stats),
            "competitive_landscape": self._analyze_competitive_landscape(region_reports),
            "growth_drivers": self._identify_growth_drivers(region_reports)
        }
        
        return insights
    
    def _assess_cluster_strength(self, regional_stats: Dict) -> Dict:
        """评估产业集群强度"""
        avg_advantage = regional_stats.get('avg_advantage_score', 0)
        diversity = regional_stats.get('regional_diversity_score', 0)
        
        if avg_advantage > 0.6 and diversity > 0.1:
            strength_level = "强"
        elif avg_advantage > 0.5 and diversity > 0.05:
            strength_level = "中"
        else:
            strength_level = "弱"
        
        return {
            "strength_level": strength_level,
            "advantage_score": avg_advantage,
            "diversity_score": diversity,
            "recommendation": self._get_cluster_recommendation(strength_level)
        }
    
    def _assess_innovation_potential(self, regional_stats: Dict) -> Dict:
        """评估创新潜力"""
        avg_features = regional_stats.get('avg_quantum_features', [])
        
        if len(avg_features) >= 4:
            innovation_dimension = avg_features[0]  # 假设第1维是创新维度
            ecosystem_dimension = avg_features[2]   # 假设第3维是生态系统维度
            
            innovation_score = (innovation_dimension + ecosystem_dimension) / 2
            
            if innovation_score > 10:
                potential_level = "高"
            elif innovation_score > 5:
                potential_level = "中"
            else:
                potential_level = "低"
        else:
            innovation_score = 0
            potential_level = "未知"
        
        return {
            "potential_level": potential_level,
            "innovation_score": innovation_score,
            "key_factors": ["研发投入", "人才密度", "生态系统协同"]
        }
    
    def _analyze_competitive_landscape(self, region_reports: List[Dict]) -> Dict:
        """分析竞争格局"""
        companies = [r['report'].get('company_name', '') for r in region_reports]
        
        return {
            "total_companies": len(companies),
            "market_concentration": "中等" if len(companies) <= 5 else "分散",
            "competitive_intensity": "高" if len(companies) > 3 else "中等",
            "key_players": companies[:3]  # 前3家公司
        }
    
    def _identify_growth_drivers(self, region_reports: List[Dict]) -> List[str]:
        """识别增长驱动因素"""
        drivers = []
        
        # 分析行业分布
        industries = []
        for report in region_reports:
            if 'analysis_metadata' in report['report']:
                basic_info = report['report']['analysis_metadata'].get('company_basic_info', {})
                industry = basic_info.get('industry', '')
                if industry:
                    industries.append(industry)
        
        # 识别主要行业
        industry_counts = {}
        for industry in industries:
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        # 找出主要行业作为增长驱动
        for industry, count in industry_counts.items():
            if count >= 2:  # 至少2家公司
                drivers.append(f"{industry}产业集群")
        
        if not drivers:
            drivers = ["多元化发展", "创新驱动"]
        
        return drivers
    
    def _assess_regional_risks(self, quantum_features: List[Dict]) -> Dict:
        """评估地区风险"""
        if not quantum_features:
            return {"risk_level": "未知", "risk_factors": []}
        
        # 计算风险指标
        entanglement_strengths = [qf['entanglement_strength'] for qf in quantum_features]
        avg_entanglement = sum(entanglement_strengths) / len(entanglement_strengths)
        
        # 高关联度意味着系统性风险
        if avg_entanglement > 0.8:
            risk_level = "高"
        elif avg_entanglement > 0.6:
            risk_level = "中"
        else:
            risk_level = "低"
        
        risk_factors = []
        if avg_entanglement > 0.7:
            risk_factors.append("行业关联度过高")
        
        # 检查多样性风险
        advantage_scores = [qf['advantage_score'] for qf in quantum_features]
        advantage_std = (sum((score - sum(advantage_scores)/len(advantage_scores))**2 for score in advantage_scores) / len(advantage_scores))**0.5
        
        if advantage_std < 0.1:
            risk_factors.append("企业同质化严重")
        
        return {
            "risk_level": risk_level,
            "avg_entanglement": avg_entanglement,
            "risk_factors": risk_factors,
            "mitigation_suggestions": self._get_risk_mitigation_suggestions(risk_factors)
        }
    
    def _generate_regional_investment_recommendations(self, regional_stats: Dict) -> Dict:
        """生成地区投资建议"""
        avg_advantage = regional_stats.get('avg_advantage_score', 0)
        diversity = regional_stats.get('regional_diversity_score', 0)
        
        if avg_advantage > 0.6 and diversity > 0.1:
            recommendation = "强烈推荐"
            strategy = "重点配置该地区龙头企业"
        elif avg_advantage > 0.5:
            recommendation = "推荐"
            strategy = "选择性投资，关注差异化企业"
        else:
            recommendation = "谨慎"
            strategy = "等待更好的投资机会"
        
        return {
            "recommendation_level": recommendation,
            "investment_strategy": strategy,
            "key_metrics": {
                "avg_advantage_score": avg_advantage,
                "diversity_score": diversity
            }
        }
    
    def _get_cluster_recommendation(self, strength_level: str) -> str:
        """获取集群建议"""
        recommendations = {
            "强": "该地区产业集群优势明显，建议加大投资力度",
            "中": "产业集群有一定基础，建议选择性投资",
            "弱": "产业集群较弱，建议谨慎投资或等待时机"
        }
        return recommendations.get(strength_level, "建议进一步分析")
    
    def _get_risk_mitigation_suggestions(self, risk_factors: List[str]) -> List[str]:
        """获取风险缓解建议"""
        suggestions = []
        
        for factor in risk_factors:
            if "行业关联度过高" in factor:
                suggestions.append("建议投资组合多元化，降低行业集中度")
            elif "企业同质化严重" in factor:
                suggestions.append("建议关注差异化企业，寻找独特竞争优势")
        
        if not suggestions:
            suggestions.append("当前风险可控，建议持续监控")
        
        return suggestions
    
    def save_regional_report(self, regional_report: Dict, output_path: str):
        """保存地区报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(regional_report, f, ensure_ascii=False, indent=2)
        
        print(f"地区报告已保存至: {output_path}")
    
    def process_region(self, directory_path: str, region_name: str, output_path: str = None):
        """
        处理指定地区的公司报告并生成地区报告
        
        Args:
            directory_path: 公司报告目录
            region_name: 目标地区名称
            output_path: 输出文件路径，如果为None则自动生成
        """
        # 加载公司报告
        company_reports = self.load_company_reports(directory_path, region_name)
        
        if not company_reports:
            print(f"未找到地区 {region_name} 的公司报告")
            return None
        
        # 按地区分组
        region_groups = self.group_by_region(company_reports)
        
        if region_name not in region_groups:
            print(f"未找到地区 {region_name} 的公司报告")
            return None
        
        # 生成地区报告
        regional_report = self.generate_regional_report(region_groups[region_name], region_name)
        
        # 保存报告
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"regional_report_{region_name.replace('，', '_')}_{timestamp}.json"
        
        self.save_regional_report(regional_report, output_path)
        
        return regional_report 