from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
import os
import json
from pathlib import Path
from crewai.tools import BaseTool

class JsonReaderTool(BaseTool):
    name: str = "json_reader_tool"
    description: str = "Reads a local JSON file and returns its contents"

    def _run(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            return "JSON_FILE_NOT_FOUND"

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return f"JSON_READ_ERROR: {str(e)}"

        # CrewAI requires string output
        return json.dumps(data, indent=2)





@CrewBase
class V1():
    """V1 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
#####################################################################
    @agent
    def semantic_interpreter(self) -> Agent:
        return Agent(
            config=self.agents_config['semantic_interpreter'], # type: ignore[index]
            tools=[JsonReaderTool()],
            verbose=True,
            # llm_config = {
            #     "model": "openrouter/tngtech/tng-r1t-chimera:free",
            #     "api_key": os.getenv("OPENROUTER_API_KEY"),
            #     "temperature": 0.1,
            #     "top_p" : 0.1
            # }
        )

    @agent
    def Dataset_Writer(self) -> Agent:
        return Agent(
            config=self.agents_config['Dataset_Writer'], # type: ignore[index]
            verbose=True,
            # llm_config = {
            #     "model": "openrouter/tngtech/tng-r1t-chimera:free",
            #     "api_key": os.getenv("OPENROUTER_API_KEY"),
            #     "temperature": 0.0,
            #     "top_p" : 0.1
            # }
        )

######################################################################
    @task
    def feature_conversion_task(self) -> Task:
        return Task(
            config=self.tasks_config['feature_conversion_task'], # type: ignore[index]
            output_file='feature_understanding.md'
        )

    @task
    def generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['generation_task'], # type: ignore[index]
            output_file='dataset1.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the V1 crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
