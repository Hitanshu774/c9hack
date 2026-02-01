from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
from crewai.tools import tool
from tools.team_features_tool import load_semantic_state





@CrewBase
class V1():
    """V1 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @tool("load_team_semantics")
    def load_team_semantics() -> dict:
        """Load frozen team strategy semantics from JSON."""
        return load_semantic_state()
#####################################################################
    @agent
    def semantic_interpreter(self) -> Agent:
        return Agent(
            config=self.agents_config['semantic_interpreter'], # type: ignore[index]
            verbose=True
        )

    @agent
    def Dataset_Writer(self) -> Agent:
        return Agent(
            config=self.agents_config['dataset_generator'], # type: ignore[index]
            verbose=True
        )

######################################################################
    @task
    def feature_conversion_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            output_file='feature_understanding.md'
        )

    @task
    def generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
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
