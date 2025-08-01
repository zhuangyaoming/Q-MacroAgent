import pandas as pd

def load_data(data_path):
    df = pd.read_csv(data_path)
    # 自动识别因子列（排除公司、简称、时间、path-weight）
    factor_cols = [col for col in df.columns if col not in ['company', 'Accper', 'path_weights']]
    factors = factor_cols
    path_weights = df['path_weights'] if 'path_weights' in df else None
    # time_series: 按公司、时间组织的因子数值
    time_series = df[['company', 'Accper'] + factor_cols]
    return factors, path_weights, time_series, df