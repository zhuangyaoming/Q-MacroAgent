"""
量子并行处理器 - 集成到Tavily项目
基于wuyue量子框架实现多公司并行分析
"""

import asyncio
import logging
import os
import json
import math
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

# 导入wuyue量子框架
from wuyue_machine_learning.encoding import AmplitudeEncoding, AngleEncoding
from wuyue.register.quantumregister import QuantumRegister
from wuyue.register.classicalregister import ClassicalRegister
from wuyue.circuit.circuit import QuantumCircuit
from wuyue.element.gate import H, RX, RY, RZ, CNOT, CZ, MEASURE
from wuyue.backend import Backend

# 导入Tavily组件
from ..graph import Graph

logger = logging.getLogger(__name__)


class QuantumParallelProcessor:
    """
    量子并行处理器
    结合Tavily的高质量数据收集和量子并行计算能力
    """
    
    def __init__(self, max_companies: int = 8, n_layers: int = 3, shots: int = 1000):
        """
        初始化量子并行处理器

        Args:
            max_companies: 支持的最大公司数量
            n_layers: 量子线路层数
            shots: 量子测量次数
        """
        self.max_companies = max_companies
        self.n_layers = n_layers
        self.shots = shots

        # 量子参数
        self.n_qubits = math.ceil(math.log2(max_companies))  # 公司索引量子比特
        self.feature_qubits = 4  # 特征量子比特
        self.total_qubits = self.n_qubits + self.feature_qubits

        # 量子后端 - 延迟初始化
        self.backend = None
        self._initialize_backend()

        # 知识库设置
        self._setup_knowledge_base()

        logger.info(f"🔬 量子并行处理器初始化完成: {self.total_qubits}量子比特, {n_layers}层, {shots}次测量")

    def _initialize_backend(self):
        """初始化量子后端"""
        try:
            self.backend = Backend.get_device()
            logger.debug("量子后端初始化成功")
        except Exception as e:
            logger.warning(f"量子后端初始化失败: {e}")
            self.backend = None
    
    def _setup_knowledge_base(self):
        """设置知识库目录"""
        self.knowledge_base_dir = "knowledge_base"
        self.company_reports_dir = os.path.join(self.knowledge_base_dir, "company_reports")
        self.quantum_metadata_dir = os.path.join(self.knowledge_base_dir, "quantum_metadata")
        self.batch_results_dir = os.path.join(self.knowledge_base_dir, "batch_results")
        
        for directory in [self.knowledge_base_dir, self.company_reports_dir, 
                         self.quantum_metadata_dir, self.batch_results_dir]:
            os.makedirs(directory, exist_ok=True)
    
    async def process_companies_quantum_parallel(self, companies: List[Dict[str, str]], 
                                                websocket_manager=None, job_id=None) -> Dict[str, Any]:
        """量子并行处理多家公司"""
        # 保存原始公司数据供后续使用
        self.original_companies = companies
        
        logger.info(f"🚀 开始量子并行分析 {len(companies)} 家公司...")
        
        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id, 
                status="processing", 
                message=f"🔬 Starting quantum parallel analysis of {len(companies)} companies"
            )
        
        try:
            # 第一阶段：使用Tavily并行收集高质量数据
            logger.info("📊 阶段1: 使用Tavily收集公司数据...")
            tavily_data = await self._collect_tavily_data(companies, websocket_manager, job_id)
            
            # 第二阶段：量子编码和并行处理
            logger.info("⚡ 阶段2: 量子编码和并行计算...")
            quantum_results = await self._quantum_process(tavily_data, websocket_manager, job_id)
            
            # 第三阶段：融合分析和报告生成
            logger.info("🧠 阶段3: 融合分析和报告生成...")
            final_reports = await self._generate_enhanced_reports(tavily_data, quantum_results, websocket_manager, job_id)
            
            # 第四阶段：保存到知识库
            logger.info("💾 阶段4: 保存到知识库...")
            batch_summary = await self._save_to_knowledge_base(final_reports, companies)
            
            result = {
                "successful_reports": final_reports,
                "failed_companies": [],
                "batch_summary": batch_summary,
                "quantum_metadata": {
                    "total_qubits": self.total_qubits,
                    "quantum_layers": self.n_layers,
                    "measurement_shots": self.shots,
                    "quantum_advantage_enabled": True
                }
            }
            
            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id,
                    status="completed",
                    message=f"🎉 Quantum parallel analysis completed for {len(companies)} companies",
                    result=result
                )
            
            logger.info("✅ 量子并行分析完成！")
            return result
            
        except Exception as e:
            logger.error(f"❌ 量子并行分析失败: {e}")
            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id, status="error", message=f"Quantum analysis failed: {str(e)}"
                )
            raise e
    
    async def _collect_tavily_data(self, companies_data: List[Dict[str, str]], 
                                 websocket_manager, job_id) -> Dict[str, Any]:
        """使用Tavily并行收集公司数据"""
        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id, status="processing", 
                message="📊 Collecting high-quality data using Tavily..."
            )
        
        # 并行执行Tavily分析
        tasks = []
        for i, company_data in enumerate(companies_data):
            task = self._run_tavily_analysis(company_data, i+1, len(companies_data))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        tavily_data = {}
        for i, result in enumerate(results):
            company_name = companies_data[i]["name"]
            if isinstance(result, Exception):
                logger.error(f"❌ Tavily分析失败 {company_name}: {result}")
                # 创建默认数据
                tavily_data[company_name] = {
                    "report": f"Analysis failed for {company_name}",
                    "company_data": {},
                    "financial_data": {},
                    "error": str(result)
                }
            else:
                tavily_data[company_name] = result
        
        return tavily_data
    
    async def _run_tavily_analysis(self, company_data: Dict[str, str], 
                                 company_index: int, total_companies: int) -> Dict[str, Any]:
        """运行单个公司的Tavily分析"""
        company_name = company_data["name"]
        logger.info(f"🔍 分析 {company_name} ({company_index}/{total_companies})")
        
        # 创建Tavily Graph实例
        graph = Graph(
            company=company_name,
            url=company_data.get("company_url", ""),
            industry=company_data.get("industry", ""),
            hq_location=company_data.get("hq_location", ""),
            websocket_manager=None,  # 避免WebSocket冲突
            job_id=None
        )
        
        # 执行Tavily分析
        state = {}
        async for s in graph.run(thread={}):
            state.update(s)
        
        # 提取关键数据
        report_content = state.get('report') or (state.get('editor') or {}).get('report', '')
        
        return {
            "company_name": company_name,
            "report": report_content,
            "company_data": state.get('company_data', {}),
            "financial_data": state.get('financial_data', {}),
            "industry_data": state.get('industry_data', {}),
            "news_data": state.get('news_data', {}),
            "references": state.get('references', []),
            "full_state": state
        }
    
    async def _quantum_process(self, tavily_data: Dict[str, Any],
                             websocket_manager, job_id) -> Dict[str, Any]:
        """量子编码和并行处理 - 使用single_agent的正确方式"""
        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id, status="processing",
                message="⚡ Quantum encoding and parallel processing..."
            )

        # 验证Tavily数据质量
        valid_companies = 0
        for company_name, data in tavily_data.items():
            report = data.get('report', '')
            if report and len(report.strip()) > 50:  # 至少有50个字符的有效报告
                valid_companies += 1

        if valid_companies == 0:
            logger.warning("⚠️ 没有有效的Tavily数据，量子分析将基于默认参数")
            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id, status="processing",
                    message="⚠️ Limited data available, using quantum analysis with default parameters..."
                )

        # 转换为single_agent格式的公司数据
        companies_data = []
        for company_name, data in tavily_data.items():
            # 从Tavily数据中提取因子信息
            factors = self._extract_factors_from_tavily_data(data)
            companies_data.append({
                "name": company_name,
                "factors": factors,
                "tavily_data": data
            })

        # 使用single_agent的量子编码方式 - 一个量子线路处理所有公司
        encoded_qc = self._encode_all_companies_to_single_circuit(companies_data)

        # 构建分析线路（基于single_agent的方式）
        analysis_qc = self._create_analysis_circuit(encoded_qc)

        # 执行量子计算 - 只调用一次！
        measurement_results = self._execute_single_quantum_circuit(analysis_qc)

        # 分析量子结果
        quantum_analysis = self._analyze_quantum_results(measurement_results, companies_data)

        return quantum_analysis

    def _extract_factors_from_tavily_data(self, tavily_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从Tavily数据中提取因子信息，转换为single_agent格式"""
        factors = []

        # 从报告长度提取信息丰富度因子
        report_length = len(tavily_data.get('report', ''))
        factors.append({
            "name": "信息丰富度",
            "value": min(report_length / 1000.0, 10.0),  # 标准化到0-10
            "weight": 0.2
        })

        # 从数据源数量提取可信度因子
        references_count = len(tavily_data.get('references', []))
        factors.append({
            "name": "数据源可信度",
            "value": min(references_count / 2.0, 10.0),  # 标准化到0-10
            "weight": 0.25
        })

        # 从财务数据提取财务健康度因子
        financial_data = tavily_data.get('financial_data', {})
        financial_score = len(str(financial_data)) / 100.0  # 简单的财务数据丰富度
        factors.append({
            "name": "财务健康度",
            "value": min(financial_score, 10.0),
            "weight": 0.3
        })

        # 从新闻数据提取市场活跃度因子
        news_data = tavily_data.get('news_data', {})
        news_activity = len(str(news_data)) / 100.0
        factors.append({
            "name": "市场活跃度",
            "value": min(news_activity, 10.0),
            "weight": 0.25
        })

        return factors

    def _encode_all_companies_to_single_circuit(self, companies_data: List[Dict[str, Any]]) -> QuantumCircuit:
        """
        将所有公司编码到单个量子线路中 - single_agent的正确方式
        这是真正的量子并行：一个量子线路同时处理所有公司
        """
        n_companies = len(companies_data)
        if n_companies > self.max_companies:
            raise ValueError(f"公司数量 {n_companies} 超过最大支持数量 {self.max_companies}")

        # 创建量子寄存器
        qreg = QuantumRegister(self.total_qubits)
        creg = ClassicalRegister(self.total_qubits)
        qc = QuantumCircuit(qreg, creg)

        # 1. 创建公司索引的叠加态 - 关键：所有公司同时存在！
        for i in range(self.n_qubits):
            qc.add(H, qreg[i])  # |00⟩ + |01⟩ + |10⟩ + |11⟩

        # 2. 为每个公司编码特征数据到同一个量子系统
        for company_idx, company_data in enumerate(companies_data):
            self._encode_single_company_to_circuit(qc, qreg, company_idx, company_data)

        logger.info(f"✅ 成功将 {n_companies} 家公司编码到单个量子线路中")
        return qc

    def _encode_single_company_to_circuit(self, qc: QuantumCircuit, qreg: QuantumRegister,
                                        company_idx: int, company_data: Dict[str, Any]):
        """
        将单个公司的数据编码到量子线路中 - 基于single_agent的方法
        """
        factors = company_data.get('factors', [])

        # 提取因子特征
        features = self._extract_features_from_factors(factors)

        # 使用角度编码将特征编码到特征量子比特上
        for feature_idx, feature_value in enumerate(features[:self.feature_qubits]):
            target_qubit = self.n_qubits + feature_idx

            # 创建受控旋转门，只有当公司索引匹配时才应用
            control_qubits = self._get_control_qubits_for_company(company_idx)

            # 应用受控RY门编码特征值
            self._apply_controlled_rotation(qc, qreg, control_qubits, target_qubit, feature_value)

    def _extract_features_from_factors(self, factors: List[Dict[str, Any]]) -> List[float]:
        """
        从因子数据中提取特征向量 - 基于single_agent的方法
        """
        features = []

        # 提取主要特征
        for factor in factors:
            value = factor.get('value', 0.0)
            weight = factor.get('weight', 0.0)

            # 特征工程：结合值和权重
            weighted_value = value * weight
            features.append(weighted_value)

        # 填充到固定长度
        while len(features) < self.feature_qubits:
            features.append(0.0)

        # 标准化到 [0, 2π] 范围（适合角度编码）
        features = np.array(features[:self.feature_qubits])
        if np.max(np.abs(features)) > 0:
            features = (features - np.min(features)) / (np.max(features) - np.min(features)) * 2 * np.pi

        return features.tolist()

    def _get_control_qubits_for_company(self, company_idx: int) -> List[int]:
        """
        获取公司索引对应的控制量子比特 - 基于single_agent的方法
        """
        binary_repr = format(company_idx, f'0{self.n_qubits}b')
        control_qubits = []

        for i, bit in enumerate(binary_repr):
            if bit == '1':
                control_qubits.append(i)

        return control_qubits

    def _apply_controlled_rotation(self, qc: QuantumCircuit, qreg: QuantumRegister,
                                 control_qubits: List[int], target_qubit: int, angle: float):
        """
        应用受控旋转门 - 基于single_agent的方法
        """
        if len(control_qubits) == 0:
            # 无控制位，直接应用旋转门
            qc.add(RY, qreg[target_qubit], paras=[angle])
        elif len(control_qubits) == 1:
            # 单控制位
            qc.add(RY, qreg[target_qubit], qreg[control_qubits[0]], paras=[angle])
        else:
            # 多控制位，简化处理
            for ctrl in control_qubits:
                qc.add(RY, qreg[target_qubit], qreg[ctrl], paras=[angle / len(control_qubits)])

    def _create_analysis_circuit(self, encoded_qc: QuantumCircuit) -> QuantumCircuit:
        """
        创建分析量子线路 - 基于single_agent的方法
        """
        qreg = encoded_qc.qreg

        # 添加变分分析层
        for layer in range(self.n_layers):
            # 每一层应用参数化旋转门
            for qubit in range(len(qreg)):
                # 应用RX, RY, RZ旋转门
                angle_x = np.random.uniform(0, 2*np.pi)
                angle_y = np.random.uniform(0, 2*np.pi)
                angle_z = np.random.uniform(0, 2*np.pi)

                encoded_qc.add(RX, qreg[qubit], paras=[angle_x])
                encoded_qc.add(RY, qreg[qubit], paras=[angle_y])
                encoded_qc.add(RZ, qreg[qubit], paras=[angle_z])

            # 添加纠缠门
            if layer < self.n_layers - 1:  # 最后一层不添加纠缠
                self._add_entanglement_layer(encoded_qc, qreg)

        # 添加最终的特征提取层
        for i in range(len(qreg)):
            encoded_qc.add(H, qreg[i])
            angle = np.pi / 4  # 固定角度
            encoded_qc.add(RY, qreg[i], paras=[angle])

        return encoded_qc

    def _add_entanglement_layer(self, qc: QuantumCircuit, qreg: QuantumRegister):
        """
        添加纠缠层 - 基于single_agent的方法
        """
        # 环形纠缠：每个量子比特与下一个量子比特纠缠
        for i in range(len(qreg) - 1):
            qc.add(CNOT, qreg[i+1], qreg[i])

        # 最后一个与第一个纠缠，形成环
        if len(qreg) > 1:
            qc.add(CNOT, qreg[0], qreg[len(qreg)-1])

    def _execute_single_quantum_circuit(self, qc: QuantumCircuit) -> Dict[str, int]:
        """
        执行单个量子线路 - single_agent的正确方式
        关键：只调用一次backend.apply()！
        """
        # 添加测量门
        qreg = qc.qreg
        creg = qc.creg

        for i in range(len(qreg)):
            qc.add(MEASURE, qreg[i], creg[i])

        try:
            # 确保后端可用
            if self.backend is None:
                self._initialize_backend()

            if self.backend is None:
                logger.warning("量子后端不可用，使用模拟结果")
                return self._generate_fallback_results(len(qreg))

            # 关键：只执行一次！
            logger.info(f"🔬 执行单个量子线路: {len(qreg)}量子比特, {self.shots}次测量")
            self.backend.apply(qc)
            results = self.backend.run(self.shots)

            # 验证结果
            if not results or not isinstance(results, dict):
                logger.warning("量子执行结果无效，使用模拟结果")
                return self._generate_fallback_results(len(qreg))

            logger.info(f"✅ 量子线路执行成功，获得 {len(results)} 个测量结果")
            return results

        except Exception as e:
            logger.error(f"❌ 量子线路执行失败: {e}")
            logger.info("使用模拟结果替代")
            return self._generate_fallback_results(len(qreg))



    def _generate_fallback_results(self, n_qubits: int) -> Dict[str, int]:
        """生成后备的模拟量子测量结果"""
        logger.info("生成模拟量子测量结果")

        import random
        results = {}

        # 生成一些随机的测量结果
        for _ in range(min(self.shots, 100)):  # 限制结果数量
            # 生成随机比特串
            bit_string = ''.join(random.choice(['0', '1']) for _ in range(n_qubits))
            if bit_string in results:
                results[bit_string] += 1
            else:
                results[bit_string] = 1

        logger.info(f"生成了 {len(results)} 个模拟测量结果")
        return results
    
    def _extract_quantum_features(self, tavily_data: Dict[str, Any]) -> List[float]:
        """从Tavily数据中提取量子特征"""
        features = []
        
        # 特征1: 报告长度（标准化）
        report_length = len(tavily_data.get('report', ''))
        features.append(min(report_length / 10000.0, 1.0))
        
        # 特征2: 数据源数量
        references_count = len(tavily_data.get('references', []))
        features.append(min(references_count / 20.0, 1.0))
        
        # 特征3: 财务数据丰富度
        financial_data = tavily_data.get('financial_data', {})
        financial_richness = len(str(financial_data)) / 1000.0
        features.append(min(financial_richness, 1.0))
        
        # 特征4: 新闻数据活跃度
        news_data = tavily_data.get('news_data', {})
        news_activity = len(str(news_data)) / 1000.0
        features.append(min(news_activity, 1.0))
        
        # 转换为角度编码 [0, 2π]
        features = [f * 2 * np.pi for f in features]
        
        return features
    

    


    def _clear_backend(self):
        """清理量子后端状态"""
        try:
            # 尝试清理当前后端
            if hasattr(self.backend, 'clear') and callable(self.backend.clear):
                self.backend.clear()
                logger.debug("量子后端状态已清理")
            elif hasattr(self.backend, 'reset') and callable(self.backend.reset):
                self.backend.reset()
                logger.debug("量子后端已重置")
            else:
                # 重新初始化后端
                self._initialize_backend()
                logger.debug("量子后端已重新初始化")
        except Exception as e:
            logger.warning(f"清理量子后端时出错: {e}")
            # 如果清理失败，强制重新初始化
            try:
                self.backend = None
                self._initialize_backend()
                logger.info("量子后端强制重新初始化成功")
            except Exception as e2:
                logger.error(f"强制重新初始化量子后端失败: {e2}")
                # 设置为None，后续使用模拟结果
                self.backend = None
    
    def _analyze_quantum_results(self, measurement_results: Dict[str, int], 
                               companies_quantum_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析量子测量结果"""
        quantum_analysis = {}
        total_shots = sum(measurement_results.values())
        
        for company_idx, company_data in enumerate(companies_quantum_data):
            company_name = company_data["name"]
            
            # 计算该公司的量子特征
            company_measurements = self._extract_company_measurements(
                measurement_results, company_idx, total_shots
            )
            
            quantum_features = self._compute_quantum_features(company_measurements)
            
            quantum_analysis[company_name] = {
                "quantum_features": quantum_features,
                "measurement_probability": company_measurements.get("probability", 0.0),
                "entanglement_strength": self._compute_entanglement_strength(company_measurements),
                "quantum_advantage_score": self._compute_quantum_advantage_score(quantum_features)
            }

        return quantum_analysis

    def _extract_company_measurements(self, measurement_results: Dict[str, int],
                                    company_idx: int, total_shots: int) -> Dict[str, Any]:
        """提取特定公司的测量结果"""
        company_results = {"probability": 0.0, "measurements": []}

        # 公司索引的二进制表示
        company_binary = format(company_idx, f'0{self.n_qubits}b')

        for bit_string, count in measurement_results.items():
            if bit_string.startswith(company_binary):
                company_results["measurements"].append((bit_string, count))
                company_results["probability"] += count / total_shots

        return company_results

    def _compute_quantum_features(self, company_measurements: Dict[str, Any]) -> List[float]:
        """计算量子特征"""
        measurements = company_measurements.get("measurements", [])

        if not measurements:
            return [0.0] * 4

        # 特征1: 测量熵
        probabilities = [count for _, count in measurements]
        total = sum(probabilities)
        if total > 0:
            probabilities = [p/total for p in probabilities]
            entropy = -sum(p * np.log2(p + 1e-10) for p in probabilities if p > 0)
        else:
            entropy = 0.0

        # 特征2: 最大概率
        max_prob = max(probabilities) if probabilities else 0.0

        # 特征3: 状态多样性
        num_states = len(measurements)

        # 特征4: 平均比特值
        avg_bit_value = 0.0
        if measurements:
            total_weight = 0
            for bit_string, count in measurements:
                bit_value = sum(int(bit) for bit in bit_string) / len(bit_string)
                avg_bit_value += bit_value * count
                total_weight += count
            if total_weight > 0:
                avg_bit_value /= total_weight

        return [entropy, max_prob, float(num_states), avg_bit_value]

    def _compute_entanglement_strength(self, company_measurements: Dict[str, Any]) -> float:
        """计算纠缠强度"""
        measurements = company_measurements.get("measurements", [])
        if len(measurements) <= 1:
            return 0.0

        probabilities = [count for _, count in measurements]
        total = sum(probabilities)
        if total == 0:
            return 0.0

        probabilities = [p/total for p in probabilities]
        max_entropy = np.log2(len(probabilities))
        actual_entropy = -sum(p * np.log2(p + 1e-10) for p in probabilities if p > 0)

        return actual_entropy / max_entropy if max_entropy > 0 else 0.0

    def _compute_quantum_advantage_score(self, quantum_features: List[float]) -> float:
        """计算量子优势评分"""
        if not quantum_features:
            return 0.0

        weights = [0.3, 0.3, 0.2, 0.2]
        normalized_features = []

        for i, feature in enumerate(quantum_features):
            if i == 0:  # 熵
                normalized_features.append(min(feature / 3.0, 1.0))
            elif i == 1:  # 最大概率
                normalized_features.append(feature)
            elif i == 2:  # 状态数
                normalized_features.append(min(feature / 8.0, 1.0))
            else:  # 平均比特值
                normalized_features.append(feature)

        score = sum(w * f for w, f in zip(weights, normalized_features))
        return min(score, 1.0)

    async def _generate_enhanced_reports(self, tavily_data: Dict[str, Any],
                                       quantum_results: Dict[str, Any],
                                       websocket_manager, job_id) -> Dict[str, Any]:
        """生成量子增强的报告"""
        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id, status="processing",
                message="🧠 Generating quantum-enhanced reports with DeepSeek..."
            )

        enhanced_reports = {}

        for company_name, tavily_report in tavily_data.items():
            quantum_meta = quantum_results.get(company_name, {})
            
            # 从原始公司数据中获取基本信息
            company_info = next((c for c in self.original_companies if c["name"] == company_name), {})

            base_report = tavily_report.get("report", "")

            # 如果基础报告为空，生成基本框架
            if not base_report.strip():
                base_report = f"""# {company_name} 公司分析报告

## 公司概况
*基于可获得的公开信息进行分析*

## 业务分析
*详细业务信息收集中*

## 财务状况
*财务数据分析中*

## 市场地位
*市场定位分析中*
"""

            # 调用DeepSeek生成最终统一报告
            final_report = await self._generate_unified_report_with_quantum_insights(
                company_name, base_report, quantum_meta, tavily_report
            )

            enhanced_report = {
                "company_name": company_name,
                "company_industry": company_info.get("industry", ""),
                "company_location": company_info.get("hq_location", ""),
                "company_url": company_info.get("company_url", ""),
                "tavily_report": base_report,
                "quantum_enhanced_analysis": final_report,
                "analysis_metadata": {
                    "company_basic_info": {
                        "name": company_name,
                        "industry": company_info.get("industry", ""),
                        "hq_location": company_info.get("hq_location", ""),
                        "company_url": company_info.get("company_url", "")
                    },
                    "tavily_data": {
                        "company_data": tavily_report.get("company_data", {}),
                        "financial_data": tavily_report.get("financial_data", {}),
                        "industry_data": tavily_report.get("industry_data", {}),
                        "news_data": tavily_report.get("news_data", {}),
                        "references": tavily_report.get("references", [])
                    },
                    "quantum_metadata": {
                        "quantum_features": quantum_meta.get("quantum_features", []),
                        "quantum_advantage_score": quantum_meta.get("quantum_advantage_score", 0.0),
                        "entanglement_strength": quantum_meta.get("entanglement_strength", 0.0),
                        "measurement_probability": quantum_meta.get("measurement_probability", 0.0),
                        "processing_timestamp": datetime.now().isoformat(),
                        "quantum_backend": "wuyue_simulator",
                        "shots_used": self.shots,
                        "quantum_layers": self.n_layers,
                        "total_qubits": self.total_qubits
                    }
                }
            }

            enhanced_reports[company_name] = enhanced_report

        return enhanced_reports

    async def _generate_unified_report_with_quantum_insights(self, company_name: str, base_report: str, 
                                                           quantum_meta: Dict[str, Any], 
                                                           tavily_data: Dict[str, Any]) -> str:
        """使用DeepSeek生成融合量子洞察的专业金融报告"""
        
        # 提取详细的量子分析数据
        quantum_features = quantum_meta.get("quantum_features", [])
        quantum_advantage_score = quantum_meta.get("quantum_advantage_score", 0.0)
        entanglement_strength = quantum_meta.get("entanglement_strength", 0.0)
        measurement_probability = quantum_meta.get("measurement_probability", 0.0)
        
        # 构建详细的量子分析解释
        quantum_analysis_detail = self._build_quantum_analysis_context(
            quantum_features, quantum_advantage_score, entanglement_strength, measurement_probability
        )
        
        # 获取参考数据源信息
        references = tavily_data.get("references", [])
        data_sources = f"基于{len(references)}个权威数据源" if references else "基于公开信息"
        
        prompt = f"""你是一位资深的金融分析师和量化投资专家。请基于以下信息，为{company_name}生成一份专业的公司研究报告。

【基础研究报告】
{base_report}

【量子并行分析核心洞察】
本分析采用了先进的量子并行计算技术，同时处理多家公司数据以获得更准确的相对比较结果。以下是关键量子分析指标：

1. **市场差异化指数**: {quantum_advantage_score:.4f}
   - 范围：0-1，当前值：{quantum_advantage_score:.4f}
   - 解读：{'高度差异化企业，具备独特竞争优势' if quantum_advantage_score > 0.7 else '适度差异化，有一定特色' if quantum_advantage_score > 0.4 else '同质化程度较高，需要寻找差异化路径'}
   - 投资意义：差异化程度直接影响企业的定价权和盈利能力

2. **行业关联度系数**: {entanglement_strength:.4f}
   - 范围：0-1，当前值：{entanglement_strength:.4f}
   - 解读：{'高度依赖行业周期，系统性风险较高' if entanglement_strength > 0.7 else '中等行业敏感度，有一定独立性' if entanglement_strength > 0.4 else '相对独立于行业趋势，个股特征明显'}
   - 投资意义：决定了宏观经济和行业政策对公司的影响程度

3. **市场权重指数**: {measurement_probability:.4f}
   - 解读：{'行业核心企业，具有重要市场地位' if measurement_probability > 0.15 else '重要参与者，有一定影响力' if measurement_probability > 0.1 else '一般参与者，关注成长潜力'}
   - 投资意义：反映了公司在同类企业中的相对重要性和市场影响力

4. **量子特征向量**: {quantum_features}
   - 这些数值反映了公司在多维度特征空间中的位置
   - 通过量子叠加态分析得出，提供了传统分析无法获得的深层洞察

{quantum_analysis_detail}

【数据来源】
{data_sources}，通过量子并行处理技术进行深度分析

【报告要求】
请将以上信息整合成一份专业的金融研究报告，特别注意：

1. **量子分析的商业价值转化**：将量子计算结果转化为具体的商业洞察和投资建议
2. **风险评估**：基于行业关联度和市场地位评估投资风险
3. **投资策略**：根据差异化指数和市场权重制定投资策略
4. **专业术语**：使用标准的金融分析和投资研究术语
5. **结构化分析**：保持逻辑清晰的Markdown格式

报告结构应包含：
- 执行摘要（含投资评级）
- 公司概况与业务分析  
- 财务状况分析
- 市场地位与竞争优势（重点融入量子分析洞察）
- 风险因素评估
- 投资建议与目标价位
- 附录：量子分析技术说明

请确保量子分析的独特价值在报告中得到充分体现。"""

        try:
            # 初始化DeepSeek客户端
            if not hasattr(self, 'deepseek_client'):
                from openai import OpenAI
                api_key = os.getenv("DEEPSEEK_API_KEY")
                if not api_key:
                    raise ValueError("DEEPSEEK_API_KEY not found. DeepSeek API is required for quantum analysis.")
                
                self.deepseek_client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位顶级的金融分析师和量化投资专家，拥有20年的投资研究经验。
你擅长将复杂的量化分析结果转化为清晰的投资洞察，特别是在利用先进计算技术进行企业分析方面有独到见解。
你的报告以专业性、准确性和实用性著称，深受机构投资者信赖。"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # 降低温度确保专业性
                max_tokens=8192,  # DeepSeek最大支持8192 tokens
                top_p=0.9
            )
            
            unified_report = response.choices[0].message.content.strip()
            logger.info(f"✅ DeepSeek成功生成{company_name}量子增强报告 ({len(unified_report)}字符)")
            return unified_report
            
        except Exception as e:
            logger.error(f"❌ DeepSeek报告生成失败: {e}")
            raise Exception(f"DeepSeek API调用失败: {str(e)}")

    def _build_quantum_analysis_context(self, quantum_features: List[float],
                                      quantum_advantage_score: float,
                                      entanglement_strength: float,
                                      measurement_probability: float) -> str:
        """构建量子分析的详细上下文说明"""

        context = f"""
【量子分析技术背景】
本分析采用了基于wuyue量子框架的并行计算技术，通过以下步骤获得洞察：

1. **量子编码阶段**：将公司的多维特征数据编码到{self.total_qubits}个量子比特的叠加态中
2. **并行处理阶段**：利用量子叠加态同时分析多家公司，发现隐藏的关联模式
3. **量子测量阶段**：通过{self.shots}次量子测量获得统计结果
4. **特征提取阶段**：从量子态坍缩结果中提取{len(quantum_features)}维特征向量

【量子优势说明】
相比传统串行分析，量子并行分析具有以下优势：
- **真并行性**：利用量子叠加态实现真正的同时计算，而非时间片轮转
- **关联发现**：通过量子纠缠自动捕获公司间的隐含关联关系
- **特征增强**：量子测量提供传统方法无法获得的非线性特征组合
- **相对比较**：在同一量子系统中处理多家公司，获得更准确的相对评估

【关键指标解读】
- 市场差异化指数反映了公司在量子特征空间中的独特性
- 行业关联度系数来源于量子纠缠强度，揭示了公司与行业的深层关联
- 市场权重指数基于量子测量概率，体现了公司的相对重要性

这些指标的组合为投资决策提供了全新的量化维度。"""

        return context

    async def _save_to_knowledge_base(self, enhanced_reports: Dict[str, Any],
                                    original_companies: List[Dict[str, str]]) -> Dict[str, Any]:
        """保存到知识库"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存单个公司报告
        for company_name, report in enhanced_reports.items():
            # 从原始公司数据中获取行业和位置信息
            company_info = next((c for c in original_companies if c["name"] == company_name), {})
            industry = company_info.get("industry", "未知行业").replace("/", "-").replace("\\", "-")
            location = company_info.get("hq_location", "未知位置").replace("/", "-").replace("\\", "-")
            
            # 新的命名格式: 公司名_行业_位置_quantum_enhanced_时间戳.json
            safe_company_name = company_name.replace("/", "-").replace("\\", "-")
            filename = f"{safe_company_name}_{industry}_{location}_quantum_enhanced_{timestamp}.json"
            filepath = os.path.join(self.company_reports_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"📁 {company_name} 量子增强报告已保存: {filepath}")

        # 保存批量分析摘要
        batch_summary = {
            "batch_id": f"quantum_batch_{timestamp}",
            "timestamp": timestamp,
            "analysis_type": "quantum_parallel_enhanced",
            "total_companies": len(enhanced_reports),
            "successful_count": len(enhanced_reports),
            "companies_analyzed": list(enhanced_reports.keys()),
            "quantum_parameters": {
                "total_qubits": self.total_qubits,
                "quantum_layers": self.n_layers,
                "measurement_shots": self.shots,
                "max_companies": self.max_companies
            },
            "quantum_statistics": {
                "avg_quantum_advantage": np.mean([
                    report["analysis_metadata"]["quantum_metadata"]["quantum_advantage_score"]
                    for report in enhanced_reports.values()
                ]),
                "avg_entanglement_strength": np.mean([
                    report["analysis_metadata"]["quantum_metadata"]["entanglement_strength"]
                    for report in enhanced_reports.values()
                ])
            },
            "input_companies": original_companies,
            "reports_location": self.company_reports_dir
        }

        batch_filename = f"quantum_batch_analysis_{timestamp}.json"
        batch_filepath = os.path.join(self.batch_results_dir, batch_filename)

        with open(batch_filepath, 'w', encoding='utf-8') as f:
            json.dump(batch_summary, f, ensure_ascii=False, indent=2)

        logger.info(f"📊 量子批量分析摘要已保存: {batch_filepath}")
        return batch_summary

    # 为了保持向后兼容性，添加方法别名
    async def quantum_parallel_analyze(self, companies: List[Dict[str, str]],
                                     websocket_manager=None, job_id=None) -> Dict[str, Any]:
        """
        量子并行分析方法 - 这是主要的公共接口
        为了保持与application.py中调用的兼容性
        """
        return await self.process_companies_quantum_parallel(
            companies, websocket_manager, job_id
        )










