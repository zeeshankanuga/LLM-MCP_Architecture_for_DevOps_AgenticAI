from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
import asyncio


async def main():
    client = MultiServerMCPClient(
        {
            "docker-mcp" : {
            "transport": "stdio",
            "command":"python3",
            "args":["mcp_server.py"]
            }

        }
    )
    tools = await client.get_tools()    # MCP tools

    llm = ChatOllama(     #LLM 
    model="gemma4:e4b",
    temperature="0.8"
    )

    # agent with MCP tools
    agent = create_agent(
    llm,
    tools
    )

    response = await agent.ainvoke ({"messages" : 
                [
                        {'role': 'user',
                         'content': "how many containers are running",}
                    ]
                    })

    print(response['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())