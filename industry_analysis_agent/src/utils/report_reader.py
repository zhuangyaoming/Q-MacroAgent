def extract_industry(report: dict) -> str:
    return report.get("company_industry", "未知行业")

def read_reports(report_files: list) -> list:
    import json
    reports = []
    for file in report_files:
        reports.append(json.load(file))
    return reports