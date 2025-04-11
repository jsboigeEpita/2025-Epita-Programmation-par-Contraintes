import streamlit as st
import os
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.runnables import RunnableConfig
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts.chat import ChatPromptTemplate

from tool import student_project_allocation_tool, generate_image_from_allocation
from main import student_project_allocation


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. Please set it to use the OpenAI API."
    )

OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", None)
OPENAI_ENDPOINT_NAME = os.environ.get("OPENAI_ENDPOINT_NAME", "gpt-4o-mini")


ASSISTANT_ICON = "csp_image.jpg"
USER_ICON = "user_image.jpg"
# Add a title to the app
st.title("CSP LLM")


msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs,
    return_messages=True,
    memory_key="chat_history",
    output_key="output",
)

# Initialize session state for steps and images
if "steps" not in st.session_state:
    st.session_state.steps = {}
if "images" not in st.session_state:
    st.session_state.images = {}

if len(msgs.messages) == 0:
    msgs.clear()
    msgs.add_ai_message(
        "Hey, I'm an AI assistant specialized in mapping students to groups. Let's start chatting! 👇"
    )


avatars = {"human": USER_ICON, "ai": ASSISTANT_ICON}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type], avatar=avatars[msg.type]):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(
                f"**{step[0].tool}**: {step[0].tool_input}", state="complete"
            ):
                st.write(step[0].log)
                st.write(step[1])

        # Display the message content
        st.write(msg.content)

        # Display saved image if any
        if (
            str(idx) in st.session_state.images
            and st.session_state.images[str(idx)] is not None
        ):
            st.image(
                st.session_state.images[str(idx)],
                caption="Allocation Graph",
                use_container_width=True,
            )


instructions = """
You are an expert assistant specializing in student-project allocation problems using constraint satisfaction.

Your primary capabilities:
1. You help allocate students to projects based on their preferences, project capacities, and additional constraints.
2. You benchmark multiple allocation algorithms (CP-SAT, Greedy, Random) and select the best solution.
3. You can explain the allocation results clearly, including visualization through tables.
4. You provide insights on how well the allocation satisfies student preferences.

When users interact with you:
- Extract clear information about students, projects, preferences, and capacities from their descriptions.
- Present benchmarking results for different allocation algorithms.
- Explain which algorithm performed best and why.
- Provide detailed allocation results with preference satisfaction metrics. You should give the percentage of satisfaction (how many got their first choice, second and third).
- Provide the benchmarking information in a structured format, like a table.
- Use concrete examples when explaining concepts.

If no valid allocation can be found:
- Explain why the constraints might be too restrictive.
- Suggest possible modifications to make the problem solvable.

Be precise and helpful, focus on delivering clear explanations of allocation problems and their solutions.
"""


if prompt := st.chat_input(placeholder="Type your message here..."):
    st.chat_message("user", avatar=USER_ICON).write(prompt)

    llm = ChatOpenAI(
        model=OPENAI_ENDPOINT_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        streaming=True,
    )
    tools = [student_project_allocation_tool]
    chat_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", instructions),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, chat_prompt_template)

    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
    
    # Create a single assistant message container to display both the text response and image
    with st.chat_message("assistant", avatar=ASSISTANT_ICON) as assistant_container:
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        
        try:
            response = executor.invoke({"input": prompt}, cfg)
            st.write(response["output"])
            st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
            
            # Set the image to None for this message initially
            st.session_state.images[str(len(msgs.messages) - 1)] = None

            # Process the image within the same assistant container
            if (len(response["intermediate_steps"]) != 0 and len(response["intermediate_steps"][0]) != 0):
                first_interm = response["intermediate_steps"][0][0]
                if isinstance(first_interm, ToolAgentAction) and isinstance(first_interm.tool_input, dict):
                    students = first_interm.tool_input["students"]
                    projects = first_interm.tool_input["projects"]
                    preferences = first_interm.tool_input["preferences"]
                    project_capacities = first_interm.tool_input["project_capacities"]

                    preferences_2 = {pref["id"]: pref["list"] for pref in preferences}
                    project_capacities_2 = {cap["id"]: cap["number"] for cap in project_capacities}

                    allocation, benchmark_info = student_project_allocation(
                        students, projects, preferences_2, project_capacities_2, []
                    )

                    # Only try to display the image if we have an allocation
                    if allocation:
                        try:
                            image = generate_image_from_allocation(allocation, benchmark_info)
                            if image is not None:
                                # Store the image in session state for future rendering
                                st.session_state.images[str(len(msgs.messages) - 1)] = image
                                
                                # Display the image in the current assistant container
                                st.image(image, caption="Allocation Graph", use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate visualization: {e}")
                    else:
                        st.info("No valid allocation could be found. The constraints may be too restrictive.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
