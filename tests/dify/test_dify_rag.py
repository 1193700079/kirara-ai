# curl -X POST 'http://47.236.152.135/v1/chat-messages' \
# --header 'Authorization: Bearer {api_key}' \
# --header 'Content-Type: application/json' \
# --data-raw '{
#     "inputs": {},
#     "query": "What are the specs of the iPhone 13 Pro Max?",
#     "response_mode": "streaming",
#     "conversation_id": "",
#     "user": "abc-123",
#     "files": [
#       {
#         "type": "image",
#         "transfer_method": "remote_url",
#         "url": "https://cloud.dify.ai/logo/logo-site.png"
#       }
#     ]
# }'

import requests

# 定义目标 URL 和 API 密钥
url = "http://47.236.152.135/v1/chat-messages"
api_key = "app-QgzAtwP6ukQWmwpBAzew12j6"  # 替换为实际的 API 密钥

# 定义请求头
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 定义请求体数据
data = {
    "inputs": {},
    "query": "cypher的爱好是什么呢？",
    # "response_mode": "streaming",
    "conversation_id": "",
    "user": "abc-123",
    # "files": [
    #     {
    #         "type": "image",
    #         "transfer_method": "remote_url",
    #         "url": "https://cloud.dify.ai/logo/logo-site.png"
    #     }
    # ]
}

# 发送 POST 请求
try:
    response = requests.post(url, headers=headers, json=data)
    print(response)
    data = response.json()
    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功！")
        print("响应内容：", response.json())  # 打印 JSON 格式的响应内容
        print("响应内容：", data['answer'])  # 打印 JSON 格式的响应内容
        print("响应内容：", data['metadata']['usage'])  # 打印 JSON 格式的响应内容
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("错误信息：", response.text)  # 打印错误信息
except requests.exceptions.RequestException as e:
    print("请求过程中发生异常：", e)


# {'event': 'message', 'task_id': '1b8d1665-fa73-48b0-b526-290577991369', 'id': 'be00e27c-e520-4da9-8d60-2bb36e5de6ba', 'message_id': 'be00e27c-e520-4da9-8d60-2bb36e5de6ba', 'conversation_id': '8fa1683c-16e7-4bf9-b4c0-35ef60ef89ee', 'mode': 'chat', 'answer': 'Cypher的爱好非常广泛，包括羽毛球、篮球、骑行、游泳、写代码（尤其是AI相关领域）、唱歌和刷B站等。他还注重健康，正在积极护肤和健身减脂增肌。', 'metadata': {'retriever_resources': [{'dataset_id': '7149d359-e0e2-4512-95d5-fe24906a0935', 'dataset_name': 'cypher_intro.txt...', 'document_id': '8eb6374c-86b6-46a6-86e8-89c86ed14ecf', 'document_name': 'cypher_intro.txt', 'data_source_type': 'upload_file', 'segment_id': 'cbe02918-e2e5-4e6b-8985-26dadf57035e', 'retriever_from': 'api', 'score': 0.40463519389999997, 'doc_metadata': None, 'content': '### Cypher 的个人简介与生活哲学', 'position': 1}, {'dataset_id': '7149d359-e0e2-4512-95d5-fe24906a0935', 'dataset_name': 'cypher_intro.txt...', 'document_id': '8eb6374c-86b6-46a6-86e8-89c86ed14ecf', 'document_name': 'cypher_intro.txt', 'data_source_type': 'upload_file', 'segment_id': '51dfc121-1eb7-4f3a-b60b-274a9a5dfcaf', 'retriever_from': 'api', 'score': 0.3978746149, 'doc_metadata': None, 'content': '#### 基本信息\nCypher，中文名杨瑞卿，国籍为中国，摩羯座。身高184cm，体重82kg，是一个热爱生活、注重自我提升的年轻人。他的兴趣爱好广泛，包括羽毛球、篮球、骑行、游泳、写代码（尤其是AI相关领域）、唱歌、刷B站等。他目前正在积极护肤和健身减脂增肌，同时计划通过兼职和存钱来实现更好的生活质量。', 'position': 2}, {'dataset_id': '7149d359-e0e2-4512-95d5-fe24906a0935', 'dataset_name': 'cypher_intro.txt...', 'document_id': '8eb6374c-86b6-46a6-86e8-89c86ed14ecf', 'document_name': 'cypher_intro.txt', 'data_source_type': 'upload_file', 'segment_id': '8833b58b-6653-465a-a9eb-75952882a67f', 'retriever_from': 'api', 'score': 0.38630247599999995, 'doc_metadata': None, 'content': '#### 生活方式与兴趣爱好\nCypher的生活方式体现了他对健康、学习和自我管理的高度重视。以下是他的主要兴趣爱好和生活方式特点：', 'position': 3}], 'usage': {'prompt_tokens': 238, 'prompt_unit_price': '0.016', 'prompt_price_unit': '0.001', 'prompt_price': '0.003808', 'completion_tokens': 46, 'completion_unit_price': '0.048', 'completion_price_unit': '0.001', 'completion_price': '0.002208', 'total_tokens': 284, 'total_price': '0.006016', 'currency': 'RMB', 'latency': 1.8230024330114247}}, 'created_at': 1744957115}