from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from customer_support.runtime import (
    LOG_PATH,
    OUTPUT_REPORT_PATH,
    build_llm,
    build_support_search_tool,
    build_task_progress_logger,
)


@CrewBase
class CustomerSupport:
    """Customer support triage crew."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def classifier_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["classifier_agent"],  # type: ignore[index]
            tools=[build_support_search_tool()],
            verbose=False,
            allow_delegation=False,
            llm=build_llm(),
        )

    @agent
    def priority_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["priority_agent"],  # type: ignore[index]
            tools=[build_support_search_tool()],
            verbose=False,
            allow_delegation=False,
            llm=build_llm(),
        )

    @agent
    def routing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["routing_agent"],  # type: ignore[index]
            tools=[build_support_search_tool()],
            verbose=False,
            allow_delegation=False,
            llm=build_llm(),
        )

    @agent
    def supervisor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["supervisor_agent"],  # type: ignore[index]
            tools=[build_support_search_tool()],
            verbose=False,
            allow_delegation=False,
            llm=build_llm(),
        )

    @task
    def classify_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config["classify_ticket_task"],  # type: ignore[index]
        )

    @task
    def assign_priority_task(self) -> Task:
        return Task(
            config=self.tasks_config["assign_priority_task"],  # type: ignore[index]
            context=[self.classify_ticket_task()],
        )

    @task
    def route_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config["route_ticket_task"],  # type: ignore[index]
            context=[self.classify_ticket_task(), self.assign_priority_task()],
        )

    @task
    def supervisor_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["supervisor_review_task"],  # type: ignore[index]
            context=[
                self.classify_ticket_task(),
                self.assign_priority_task(),
                self.route_ticket_task(),
            ],
            output_file=str(OUTPUT_REPORT_PATH),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            output_log_file=str(LOG_PATH),
            task_callback=build_task_progress_logger(
                [
                    task.name or f"Task {index}"
                    for index, task in enumerate(self.tasks, start=1)
                ]
            ),
        )
