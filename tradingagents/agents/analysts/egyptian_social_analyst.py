"""
Egyptian Social Media Analyst
Generates social sentiment for EGX stocks using OpenAI web search tools
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_egyptian_social_analyst(llm, toolkit):
    """
    Create an Egyptian social media analyst specialized in EGX stocks

    Returns a node that writes to `sentiment_report` in the shared state.
    """

    def egyptian_social_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [toolkit.get_egyptian_social_sentiment_openai]

        system_message = (
            "You are an Egyptian social media sentiment analyst focusing on EGX-listed companies."
            " Use the provided tools to collect recent social posts and infer sentiment and key themes."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The current company we want to analyze is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return egyptian_social_analyst_node



