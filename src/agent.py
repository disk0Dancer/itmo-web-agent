from typing import Annotated

from langchain_openai import ChatOpenAI
# from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# from langchain.embeddings import init_embeddings
# from langgraph.store.memory import InMemoryStore

from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

import feedparser
from pydantic import HttpUrl
from typing import List
from typing_extensions import TypedDict

from src.schemas.request import AgentOutput

model = "gpt-4o-mini"
llm = ChatOpenAI(
    model=model,
    max_retries=2,
)
llm_struct = llm.with_structured_output(AgentOutput)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    # user_query: str
    # sources: List[str]
    # ready_to_send: bool = False
    # answer: int


@tool
def get_latest_news_tool(tool_call_id: str):
    """Возвращает последние новости ИТМО из RSS-ленты."""

    def fetch_itmo_news(max_results: int = 3) -> List[HttpUrl]:
        rss_url = "https://Itmo.ru/rss"
        feed = feedparser.parse(rss_url)
        return [HttpUrl(entry.link) for entry in feed.entries[:max_results]]

    news_links = fetch_itmo_news()
    return ToolMessage(content=", ".join(news_links), tool_call_id=tool_call_id)


search_tool = TavilySearchResults(
    max_results=3,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=False,
    include_images=False,
    # include_domains=["https://itmo.ru/", "https://news.itmo.ru/"],
    # name="Поисковой инструмент фактов в интернете",
    # description="используй инструмент чтобы получить информацию об университете итмо",
)


@tool
async def llm_tool(tool_call_id: str):
    """использовать для формирования классного текста, описания причины, форматирования результата"""
    response = await llm.ainvoke(tool_call_id)
    return response


async def reasoning_summary(messages):
    """Return reasoning for answer, make summary for all steps"""
    return await llm.ainvoke(
        f"make a summary why agent responded with selcted answer, thoughts process below:\n{process_msgs(messages)}"
    )


def process_msgs(x):
    return "\n".join([f"{i}. {msg.type} {msg.content}" for i, msg in enumerate(x)])


async def formatting(messages):
    """return user formatted data"""
    return await llm.ainvoke(
        f"respond only with digit - correct option:\n{process_msgs([messages[1], messages[-1]])}"
    )


async def get_sources(messages):
    """return sources"""
    return await llm.ainvoke(
        f"return sources urls http-like, separated by ',':\n{process_msgs(messages)}"
    )


tools = [
    llm_tool,
    search_tool,
    get_latest_news_tool,
    # reasoning_summary,
    # formatting,
]

llm_with_tools = llm.bind_tools(tools)


async def chatbot(state: State):
    message = await llm_with_tools.ainvoke(state["messages"])
    return {"messages": [message]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

memory = MemorySaver()
# store = InMemoryStore(
#     index={
#         "embed": init_embeddings("openai:text-embedding-3-small"),
#         "dims": 1536,
#     }
# )
graph = graph_builder.compile(
    checkpointer=memory,
    # store=store
)
