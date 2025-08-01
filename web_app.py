import streamlit as st
import pandas as pd
from agent.industry_agent import IndustryAgent
from agent.regional_agent import RegionalAgent
import tempfile
import os

st.set_page_config(page_title="行业智能分析", layout="wide")

st.title("行业智能分析助手")

# Tab切换：行业分析/地区分析
tabs = st.tabs(["行业分析", "地区分析"])

# ========== 行业分析 Tab ==========
with tabs[0]:
    st.write("请上传包含企业因子和关联权重的CSV文件，系统将自动进行行业趋势分析和预测。")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"], key="industry_csv")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        df = pd.read_csv(tmp_path)
        st.subheader("数据预览")
        st.dataframe(df)
        st.subheader("行业分析报告")
        with st.spinner("正在分析，请稍候..."):
            agent = IndustryAgent()
            report, graph_img_path = agent.analyze(tmp_path)
        st.success("分析完成！")
        st.markdown(f"```\n{report}\n```")
        # 可选：展示行业关系图
        # st.subheader("企业关系图可视化")
        # st.image(graph_img_path, caption="行业企业关系图")
    else:
        st.info("请先上传CSV文件。")

# ========== 地区分析 Tab ==========
with tabs[1]:
    st.write("请上传同一地区的企业json报告文件（可多选），并输入地区名称，系统将自动进行地区级企业网络与集群分析。")
    uploaded_jsons = st.file_uploader("上传企业json报告（可多选）", type=["json"], accept_multiple_files=True, key="region_jsons")
    region_name = st.text_input("请输入地区名称（如：中国，北京市）", value="中国，北京市")
    if uploaded_jsons and region_name:
        # 将上传的json文件保存到临时目录
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_paths = []
            for file in uploaded_jsons:
                file_path = os.path.join(tmp_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
                file_paths.append(file_path)
            st.write(f"已上传 {len(file_paths)} 份企业json报告")
            # 调用RegionalAgent分析
            with st.spinner("正在进行地区分析，请稍候..."):
                agent = RegionalAgent()
                # 直接传递临时目录
                report = agent.analyze_region(tmp_dir, region_name)
            if report:
                st.success("分析完成！")
                st.subheader("地区分析主要结论")
                st.markdown(f"**公司数量：** {report.get('companies_count', 0)}")
                st.markdown(f"**产业分布：** {report.get('industry_distribution', {})}")
                st.markdown(f"**产业集群强度：** {report.get('regional_insights', {}).get('economic_cluster_strength', {}).get('strength_level', '未知')}")
                st.markdown(f"**创新潜力：** {report.get('regional_insights', {}).get('innovation_potential', {}).get('potential_level', '未知')}")
                st.markdown(f"**协同分数：** {report.get('network_analysis', {}).get('synergy_score', '无')}")
                st.markdown(f"**枢纽企业：** {report.get('network_analysis', {}).get('hub_companies', [])}")
                st.markdown(f"**投资建议：** {report.get('investment_recommendations', {}).get('recommendation_level', '未知')}")
                
                # 展示LLM生成的智能分析报告
                if 'llm_report' in report:
                    st.subheader("AI智能分析报告")
                    st.markdown(report['llm_report'])
                
                # 展示网络图
                graph_img = report.get('network_analysis', {}).get('graph_image', None)
                if graph_img and os.path.exists(graph_img):
                    st.subheader("企业网络关系图（精简版）")
                    st.image(graph_img, caption="地区企业关系网络")
                # 提供txt报告下载
                txt_path = f"regional_report_{region_name.replace('，','_')}.txt"
                if os.path.exists(txt_path):
                    with open(txt_path, "r", encoding="utf-8") as f:
                        txt_content = f.read()
                    st.subheader("分析报告文本（可复制/下载）")
                    st.text_area("地区分析报告", txt_content, height=400)
                    st.download_button("下载txt报告", txt_content, file_name=txt_path)
            else:
                st.error("未生成地区分析报告，请检查数据格式或内容。")
    else:
        st.info("请上传企业json报告并输入地区名称。")

#streamlit run web_app.py