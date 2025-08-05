import requests

def call_deepseek(prompt: str) -> str:
    # 这里需替换为你的 DeepSeek API Key 和 endpoint
    api_key = "YOUR_DEEPSEEK_API_KEY"
    endpoint = "YOUR_DEEPSEEK_API_ENDPOINT"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"prompt": prompt, "max_tokens": 1024}
    response = requests.post(endpoint, headers=headers, json=payload)
    return response.json().get("result", "未获取到分析结果")