# this is the Demo2
import autogen
import os
import json
from google.colab import userdata

# API Configuracion para OpenAI
# apiConfig = [{
#        "model": "gpt-4o-mini",
#        "max_tokens": 500,
#        "api_key": os.getenv('OPENAI_API_KEY')
#    }]


# API Configuracion para Mistral -- Preferimos usar esta para las pruebas ya que no hay que pagar y es tan buena como la de OpenAI
api_config = [{
        "model": "mistral-large-latest",
        "max_tokens": 2000,
        "api_key": os.getenv('MISTRAL_API_KEY'),
        "api_type": "mistral"
    }]

# User Proxy Agent
user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
    human_input_mode="TERMINATE"
)

# Define custom temperature for each agent
product_manager_temp = 0.8   # More creative than the business analyst
business_analyst_temp = 0.6  # Less creative, more structured
coder_temp = 0.7             # Similar to the architect
architect_temp = 0.7         # Similar to the coder
qa_temp = 0.6                # Same as business analyst


# Product Manager Agent
llm_config_pm = {"config_list": api_config, "temperature": product_manager_temp, "cache_seed": 42}

pm = autogen.AssistantAgent(
    name="Product_Manager",
    system_message="You are an amazing Product Manager, creative in software product ideas, with knowledge in multiples verticals",
    llm_config=llm_config_pm,
)


# Business Analyst Agent
llm_config_ba = {"config_list": api_config, "temperature": business_analyst_temp, "cache_seed": 42}

ba = autogen.AssistantAgent(
    name="Business_Analyst",
    system_message="Act as an Expert in business analysis and requirements gathering.",
    llm_config=llm_config_ba,
)


# Architect Agent
llm_config_coder = {"config_list": api_config, "temperature": coder_temp, "cache_seed": 42}

architect = autogen.AssistantAgent(
    name="Architect",
    system_message="You are a Software Architect, with expereience in creating escalable and solid architectures, you have knowledge of Microservices and distributed monolith, as well architecture for FrontEnd in Web and Mobile. You are responsible for defining the architecture and design decisions.",
    llm_config=llm_config_coder,
)


# Coder Assistant Agent
llm_config_architect = {"config_list": api_config, "temperature": architect_temp, "cache_seed": 42}

coder = autogen.AssistantAgent(
    name="Coder",
    system_message="Act as a Staff Software Engineer.",
    llm_config=llm_config_architect,
)


# QA Agent
llm_config_qa = {"config_list": api_config, "temperature": qa_temp, "cache_seed": 42}

qa = autogen.AssistantAgent(
    name="QA",
    system_message="Expert in testing strategies, risk analysis and creating BDD specifications. You are responsible to create the Testing Plan, y Gerhkin Specifications",
    llm_config=llm_config_qa,
)

# Documentation Agent
llm_config = {"config_list": api_config, "cache_seed": 42}

class DocumentationAgent(autogen.AssistantAgent):
    def __init__(self, name, llm_config):
        super().__init__(name=name, llm_config=llm_config)
        self.final_document = {}

    def contribute(self, agent_name, section_title, content):
        # Each agent contributes to the final document
        self.final_document[agent_name] = {
            "section_title": section_title,
            "content": content
        }

    def generate_final_document(self):
        # Create documentation folder if it doesn't exist
        if not os.path.exists("documentation"):
            os.makedirs("documentation")

        # Combine all contributions into a final document
        final_content = "# Final Documentation\n\n"
        for agent_name, section in self.final_document.items():
            final_content += f"## {section['section_title']}\n\n{section['content']}\n\n"

        # Write the Markdown file
        markdown_path = "documentation/final_document.md"
        with open(markdown_path, "w") as md_file:
            md_file.write(final_content)

        print(f"Final document created in 'documentation' folder:\n- {markdown_path}")
        return markdown_path

    def self_reflect_and_improve(self, agent_name):
        # Each agent self-reflects on their contribution and suggests improvements
        reflection = f"{agent_name} self-reflects and suggests improvements on their section."
        print(f"{agent_name}: {reflection}\n")
        self.final_document[agent_name]["content"] += f"\n\n**Self-Reflection and Improvements:**\n\n{reflection}"

    def peer_review(self, agent_name, reviewer_name):
        # Each agent reviews the contribution of another agent and suggests improvements
        review = f"{reviewer_name} reviews {agent_name}'s section and suggests improvements."
        print(f"{reviewer_name}: {review}\n")
        self.final_document[agent_name]["content"] += f"\n\n**Peer Review by {reviewer_name}:**\n\n{review}"

# Instantiate the Documentation Agent
doc_agent = DocumentationAgent(
    name="Documentation_Agent",
    llm_config=llm_config
)

# GroupChat Setup with all agents
groupchat = autogen.GroupChat(agents=[user_proxy, pm, ba, architect, coder, qa, doc_agent], messages=[], max_round=12)

# GroupChat Manager to orchestrate the chat
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Function to simulate the collaboration in Phase 1
def phase_1_collaboration():
    print("Phase 1: Product Manager and Business Analyst Collaboration\n")

    # Product Manager and Business Analyst collaborate
    for agent in [pm, ba]:
        response = agent.generate_reply(groupchat.messages)
        content = response.get('content', '') if isinstance(response, dict) else response

        if agent.name == "Product_Manager":
            doc_agent.contribute(agent.name, "Product Requirements Document (PRD)", content)
        elif agent.name == "Business_Analyst":
            doc_agent.contribute(agent.name, "Business Requirements and Use Cases", content)

        print(f"{agent.name} contributed to the document in Phase 1.\n")

# Function to simulate the collaboration in Phase 2
def phase_2_collaboration():
    print("Phase 2: Coder, Architect, and QA Collaboration\n")

    # Coder and Architect work together, and QA works in parallel
    for agent in [coder, architect, qa]:
        response = agent.generate_reply(groupchat.messages)
        content = response.get('content', '') if isinstance(response, dict) else response

        if agent.name == "Coder":
            doc_agent.contribute(agent.name, "Implementation Plan", content)
        elif agent.name == "Architect":
            doc_agent.contribute(agent.name, "Architectural Decisions", content)
        elif agent.name == "QA":
            doc_agent.contribute(agent.name, "Testing Plan and BDD Specifications", content)

        print(f"{agent.name} contributed to the document in Phase 2.\n")

# Function to simulate the final revision in Phase 3
def phase_3_revision():
    print("Phase 3: Final Revision and Improvement\n")

    # Self-reflection and peer review
    for agent in groupchat.agents:
        if agent.name != "User_proxy" and agent.name != "Documentation_Agent":
            doc_agent.self_reflect_and_improve(agent.name)

    for agent in groupchat.agents:
        if agent.name != "User_proxy" and agent.name != "Documentation_Agent":
            for reviewer in groupchat.agents:
                if reviewer.name != "User_proxy" and reviewer.name != agent.name and reviewer.name != "Documentation_Agent":
                    doc_agent.peer_review(agent.name, reviewer.name)

# Function to start the conversation and generate the final document
def start_conversation():
    initial_message = "We are designing a new clone of Jira, we want to include AI in order to help with the creation of Tickets and assigning to the right person."

    groupchat.messages.append({
        "sender": user_proxy.name,
        "content": initial_message,
        "role": "user"
    })

    # Phase 1: Product Manager and Business Analyst Collaboration
    phase_1_collaboration()

    # Phase 2: Coder, Architect, and QA Collaboration
    phase_2_collaboration()

    # Phase 3: Final Revision and Improvement
    phase_3_revision()

    # Generate and deliver the final documentation
    doc_agent.generate_final_document()

# Start the group conversation
start_conversation()
