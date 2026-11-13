"""LangChain + Dataville MCP quickstart.

Connects a LangChain agent to Dataville's hosted MCP server, lists the tools
Dataville exposes, and answers one question from live SEC EDGAR and Wikipedia
data. No scrapers and no ingestion pipeline.

Docs: https://docs.dataville.com
"""

import asyncio
import os

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.mcp import MCPAdapter

SYSTEM_PROMPT = """You are a helpful assistant with access to Dataville data."""


async def main():
    config = {
        "mcpServers": {
            "dataville": {
                "url": "https://api.dataville.com/mcp",
            },
        },
    }
    if api_key := os.environ.get("DATAVILLE_API_KEY"):
        config["mcpServers"]["dataville"]["auth"] = api_key

    async with MCPAdapter(config) as adapter:
        tools = await adapter.list_tools()
        print("Dataville tools:", [tool.name for tool in tools], flush=True)

        agent = create_agent(
            init_chat_model(
                "openrouter:anthropic/claude-sonnet-4-6",
                temperature=0,
            ),
            tools,
            system_prompt=SYSTEM_PROMPT,
        )
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Use Dataville to find Nvidia's latest 10-K filing.",
                    }
                ]
            }
        )

    for message in result["messages"]:
        for call in getattr(message, "tool_calls", None) or []:
            print(f"\nTool call: {call['name']} {call['args']}")

    print("\nAnswer:\n")
    print(result["messages"][-1].text)


if __name__ == "__main__":
    asyncio.run(main())
