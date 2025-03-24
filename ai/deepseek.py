import requests
import json

class DeepSeekScheduler:
    def __init__(self, api_key, model="deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def optimize_schedule(self, schedule, constraints):
        """
        使用 DeepSeek 优化排课表
        :param schedule:  初始排课表（JSON 格式）
        :param constraints:  额外的约束（字符串）
        :return:  优化后的排课表（JSON 格式）
        """
        prompt = f"""
        你是一名智能课程调度助手，我提供一个课程安排表和优化要求，请优化课程安排：
        - **初始课程表（JSON 格式）**：
        {json.dumps(schedule, indent=2)}

        - **优化要求**：
        {constraints}

        请基于以上信息生成一个新的课程表（JSON 格式），返回格式必须保持 JSON 结构。
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(self.api_url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            return json.loads(result["choices"][0]["message"]["content"])  # 解析 JSON 输出
        else:
            raise Exception(f"DeepSeek API 调用失败: {response.status_code} {response.text}")

