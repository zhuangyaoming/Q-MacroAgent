# 行业智能分析系统

一个基于AI的行业和地区企业分析系统，支持企业关系网络分析、产业集群识别、量子特征分析等功能。

## 功能特性

### 🏭 行业分析
- 基于CSV数据的企业因子分析
- 企业关系网络构建与可视化
- 行业趋势预测与投资建议

### 🌍 地区分析  
- 多企业JSON报告整合分析
- 地区产业集群识别
- 企业协同效应量化
- 枢纽企业识别
- AI智能分析报告生成

### 📊 可视化功能
- 企业关系网络图（精简版）
- 产业集群热力图
- 量子特征向量分析

## 项目结构

```
行业agent/
├── agent/                    # 智能代理模块
│   ├── industry_agent.py    # 行业分析代理
│   └── regional_agent.py    # 地区分析代理
├── tools/                   # 工具模块
│   ├── data_loader.py       # 数据加载器
│   ├── graph_utils.py       # 图分析工具
│   ├── regional_loader.py   # 地区数据加载器
│   └── regional_graph_utils.py # 地区图分析工具
├── llm/                     # 大语言模型接口
│   └── deepseek_llm.py     # DeepSeek LLM接口
├── configs/                 # 配置模块
│   └── config.py           # 环境配置
├── data/                    # 数据目录
├── web_app.py              # Web界面
├── main.py                 # 命令行入口
└── requirements.txt        # 依赖包
```

## 安装与使用

### 1. 环境要求
- Python 3.8+
- 相关依赖包（见requirements.txt）

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
创建 `.env` 文件并配置：
```
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_API_URL=your_api_url
MODEL_NAME=your_model_name
```

### 4. 运行方式

#### Web界面
```bash
streamlit run web_app.py
```

#### 命令行
```bash
# 行业分析
python main.py data/industry_sample.csv

# 地区分析
python test_regional_agent.py
```

## 使用示例

### 行业分析
1. 准备包含企业因子和关联权重的CSV文件
2. 在Web界面选择"行业分析"Tab
3. 上传CSV文件，系统自动分析并生成报告

### 地区分析
1. 准备同一地区的多个企业JSON报告文件
2. 在Web界面选择"地区分析"Tab  
3. 上传JSON文件并输入地区名称
4. 系统自动进行地区级企业网络与集群分析

## 核心功能

### 企业关系网络分析
- 基于量子特征相似度构建企业关系图
- 识别产业集群和枢纽企业
- 计算企业协同效应分数

### AI智能分析
- 集成DeepSeek大语言模型
- 自动生成投资建议和风险分析
- 提供结构化和自然语言双重报告

### 可视化优化
- 精简版网络图，只显示重要节点联系
- 支持多种过滤参数（权重阈值、枢纽节点等）
- 中文字体自动适配

## 技术栈

- **后端**: Python, NetworkX, NumPy, Pandas
- **AI**: DeepSeek LLM, 量子特征分析
- **可视化**: Matplotlib, Graphviz
- **Web界面**: Streamlit
- **数据处理**: JSON, CSV

## 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过GitHub Issues联系。 