import os
from crewai import Agent, Task, Crew, Process, LLM

# --- IMPORT YOUR NEW TOOLS ---
from my_tools import get_uipath_job_data, query_kibana_logs

# ---
# 1. SET UP YOUR LOCAL LLM
# ---
# Model can be swapped for any model in Ollama (e.g., "ollama/mixtral", "ollama/phi3")
local_llm = LLM(
  model="ollama/llama3",
  base_url="http://localhost:11434"
)

# ---
# 2. DEFINE YOUR AGENTS
# ---

# Agent 1: UiPath Orchestrator Agent
orchestrator_agent = Agent(
  role='UiPath Orchestrator Monitor',
  goal='Fetch job and queue data from UiPath Orchestrator',
  backstory="You are an automation expert with deep API access to UiPath Orchestrator. You retrieve data accurately.",
  verbose=True,
  llm=local_llm,
  tools=[get_uipath_job_data] # Give this agent ONLY the UiPath tool
)

# Agent 2: Kibana Analyst Agent
kibana_analyst = Agent(
  role='Kibana Data Analyst',
  goal='Find and analyze logs in Kibana based on provided data',
  backstory="You are a data analyst who is an expert at writing Elasticsearch queries to find specific logs in Kibana.",
  verbose=True,
  llm=local_llm,
  tools=[query_kibana_logs] # Give this agent ONLY the Kibana tool
)

# ---
# 4. DEFINE YOUR DYNAMIC TASKS
# ---

# Task 1: Get data from UiPath
# The `{job_id}` will be filled in by the `inputs` dictionary in crew.kickoff()
task_get_job_data = Task(
  description="Fetch all details for the UiPath job with ID: {job_id}",
  expected_output="The full JSON data for the specified UiPath job.",
  agent=orchestrator_agent
)

# Task 2: Use that data to query Kibana
# This task automatically receives the output of the first task as context.
task_find_logs = Task(
  description="""Take the JSON data from the UiPath job.
  Find the 'RobotName' and 'BatchExecutionKey' from that JSON.
  Then, use your Kibana Query Tool to search for all logs
  that contain both the 'RobotName' and the 'BatchExecutionKey'.
  """,
  expected_output="A summary of the logs found in Kibana, including any error messages.",
  agent=kibana_analyst,
  context=[task_get_job_data] # This explicitly tells Task 2 to use Task 1's output
)

# ---
# 5. CREATE AND RUN THE CREW
# ---
crew = Crew(
  agents=[orchestrator_agent, kibana_analyst],
  tasks=[task_get_job_data, task_find_logs],
  process=Process.sequential,
  verbose=True
)

# --- THIS IS THE DYNAMIC PART ---
# You can change this input every time you run the script!
job_id_to_check = "00000000-0000-0000-0000-000000000001" # <-- !! PUT A REAL JOB ID HERE !!

result = crew.kickoff(inputs={'job_id': job_id_to_check})

print("\n\n########################")
print("## Here is your crew's result:")
print("########################\n")
print(result)
