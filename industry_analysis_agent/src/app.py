import streamlit as st
import json
import os
from utils.report_reader import extract_industry, read_reports
from agent import analyze_industry
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

st.title("行业分析Agent")

uploaded_files = st.file_uploader("请上传行业公司分析报告（json格式，可多选）", type="json", accept_multiple_files=True)

if uploaded_files:
    reports = []
    for file in uploaded_files:
        data = json.load(file)
        reports.append(data)
    industries = set([extract_industry(r) for r in reports])
    st.write(f"检测到行业：{', '.join(industries)}")
    if st.button("生成行业分析报告"):
        result = analyze_industry(reports)
        st.subheader("行业分析报告")
        st.write(result)