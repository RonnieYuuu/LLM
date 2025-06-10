# LLM
Here I share some interesting staff about LLM Engneering 分享一些学习大语言模型工程的一些有趣信息和做的小项目

1. (ollama)website-summarazer.py -- Site summary helper for calling locally deployed models (no api required) 调用本地部署模型的网站总结助手（无需api）

2. website-summerazer.py -- Calling the GPT API's Site Summary Assistant 使用Chatgpt API的网站内容总结助手

3. make_marketing_brochure -- Marketing brochure widget, use BeautifulSoup to crawl the company's official website content, links, etc., call ChatGPT API, analyze the content and summarize it into a brochure. 市场推广宣传手册小工具，使用BeautifulSoup爬取公司官网内容、链接等，调用ChatGPT API，分析内容，总结成宣传册。

4. ai text chatbot with memory -- 调用gpt的api，并借助gradio做的非常简单的ai文字聊天机器人，能够通过存储历史提示词记住上下文语境，更多的语境需要借助RAG技术或事提供更多的预设system prompt。
The simple ai text chatbot made by calling gpt's api and with the help of gradio. It is able to memorize the context by storing historical prompts, and more contexts need to be provided with the help of RAG technology or things to provide more preset system prompts.

5. 航班助手 FlightAI 是一个集成了 OpenAI GPT-4 Function Calling 与 Skyscanner 实时航班查询 API 的智能助手，支持自然语言输入查询任意两个城市间的机票价格，支持选择出发日期与舱位（经济/商务）。界面使用 Gradio 构建，开箱即用，可用于演示 AI 助手与实时数据接口集成的完整闭环。 ✅ 核心功能：支持自然语言输入城市、时间、舱位，自动将城市名称映射为 IATA 机场代码（待完善）、调用 Skyscanner API 获取真实航班价格（Create + Poll 模型）、集成 GPT-4 function calling 精准理解用户意图、使用 Gradio 搭建聊天界面，支持一问一答、可选展示目的地城市图片
