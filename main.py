import openai
import os

from Tools.PythonTool import xiaoyaAnalyser

from GraceAgent import (
    GraceExecutor,
    GraceGPT,
    GracePlanner
)
from Tools import *
from langchain_openai import ChatOpenAI, OpenAI
from dotenv import load_dotenv, find_dotenv
from Tools.Interpreter import Interpreter

import warnings

warnings.filterwarnings("ignore")

_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']
openai.base_url = os.environ['OPENAI_API_BASE']

def launch_agent(agent):
    human_icon = "\U0001F468"
    ai_icon = "\U0001F916"

    while True:
        task = input(
            f"{ai_icon}:您好，我是小雅，一个擅长处理医疗结构化数据的智能助理。🥳\n在提交完EHR数据之后，您可以向我尽情提出关于EHR"
            f"医疗数据的问题或者处理要求，我会根据您的需求帮您处理数据，返回相应结果辅助您更好地进行医疗数据分析。\n"
            f"现在有什么可以帮您的吗？\n{human_icon}:")
        if task.strip().lower() == "quit":
            break
        reply = agent.invoke(task, verbose=True)
        print(f"{ai_icon}:{reply}\n")


def main():
    interpreter = Interpreter()
    csv_files = ["./datasets/raw_events_data.csv", "./datasets/raw_labtest_data.csv", "./datasets/raw_target_data.csv"]
    model = ChatOpenAI(model='gpt-4-1106-preview', temperature=0, model_kwargs={"seed": 42})
    tools = [
        directory_inspection_tool,
        CSV_inspection_tool,
        finish_placeholder,
        xiaoyaAnalyser(
            model = model,
            prompt_path="./prompts/Tools",
            info_path="./Tools/xiaoya_info",
            interpreter=interpreter,
        ).as_tool()
    ]
    planner = GracePlanner(model, tools, csv_files, stop=['<END_OF_PLAN>'])
    executor = GraceExecutor(
        llm=model,
        prompts_path="prompts/executor",
        tools=tools,
        work_dir='datasets',
        main_prompt_file='executor.json',
        final_prompt_file='final_step.json',
        files=csv_files,
        max_thought_steps=10,
    )
    agent = GraceGPT(planner=planner, executor=executor)

    # 运行智能体
    launch_agent(agent)


if __name__ == "__main__":
    main()
