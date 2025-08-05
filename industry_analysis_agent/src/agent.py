import json
from src.deepseek.api import call_deepseek

def analyze_industry(reports: list) -> str:
        # 自动获取行业
        industries = set([r.get("company_industry", "未知行业") for r in reports])
        prompt = f"请基于以下{len(reports)}份公司分析报告，综合分析{', '.join(industries)}行业在不同地区的相互影响，并输出一份行业分析报告：\n"
        for i, r in enumerate(reports):
            prompt += f"\n公司{i+1}报告：\n{json.dumps(r, ensure_ascii=False)}\n"
        result = call_deepseek(prompt)
        return result

class IndustryAgent:
    def __init__(self, report_paths):
        self.reports = self.load_reports(report_paths)

    def load_reports(self, report_paths):
        reports = []
        for report_path in report_paths:
            report = self.read_reports(report_path)
            if report:
                reports.append(report)
        return reports

    def read_reports(self, report_path):
        import json
        with open(report_path, 'r') as file:
            return json.load(file)

    async def generate_industry_analysis(self):
        industry_data = self.extract_industry_data()
        insights = await self.call_deep_seek_api(industry_data)
        return self.create_analysis_report(insights)

    def extract_industry_data(self):
        industry_data = {}
        for report in self.reports:
            # Process each report to gather industry data
            pass
        return industry_data

    async def call_deep_seek_api(self, industry_data):
        from deepseek.api import call_deep_seek_api
        return await call_deep_seek_api(industry_data)

    def create_analysis_report(self, insights):
        analysis_report = {
            'insights': insights,
            # Additional fields as necessary
        }
        return analysis_report