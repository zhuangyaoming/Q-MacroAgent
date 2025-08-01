from agent.industry_agent import IndustryAgent
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python main.py <数据文件路径>")
        exit(1)
    data_path = sys.argv[1]
    agent = IndustryAgent()
    report = agent.analyze(data_path)
    print("行业分析报告：\n", report) 

    #python main.py data/industry_sample.csv