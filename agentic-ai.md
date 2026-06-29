# Agentic AI System: (MCP Server & Client)

**Author:** Zeeshan Kanuga

Built by [Zeeshan Kanuga](https://github.com/zeeshankanuga)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/zeeshankanuga/)

---

### 🎯 SITUATION: The Problem Space

**Context:**  
Modern DevOps teams manage containerized infrastructures (Docker, Kubernetes) but face a critical gap: **LLMs cannot directly execute infrastructure commands**. They hallucinate `docker ps` flags, suggest wrong `kubectl` syntax, and cannot observe real-time cluster state.

**Pain Points Identified:**
1. **No Live Access**: LLMs trained on static data (cutoff 2024-2025) cannot see *your* running containers, pod statuses, or logs
2. **Hallucination Risk**: Asking "how many containers are running?" → LLM invents a number instead of executing `docker ps -q`
3. **Tool Fragmentation**: Docker CLI, kubectl, helm — each needs different syntax; no unified interface for AI
4. **Tight Coupling**: tools were hardcoded inside the agent process — not reusable, not shareable
5. **Security Barrier**: Cannot safely expose raw shell access to AI assistants

**The Core Challenge:**  
*How to give an LLM safe, structured, real-time access to Docker via a standardized protocol — while keeping tools decoupled from the agent?*

---

### 🎯 TASK: The Objective

**Primary Goal:**  
Build a **two-component Agentic AI system** using the **Model Context Protocol (MCP)** that:
- **`mcp_server.py`**: Exposes Docker tools via stdio JSON-RPC (the *tool provider*)
- **`agent_with_mcp.py`**: Discovers and invokes those tools at runtime (the *tool consumer*)
- Runs **entirely locally** (Ollama + local MCP) — zero cloud dependency
- Enables **dynamic tool discovery** — agent learns capabilities at startup, no hardcoded tools

---

### 🛠️ ACTION: The Implementation

#### **Component 1: MCP Server — `mcp_server.py`** (The Tool Provider)

```python
from fastmcp import FastMCP
import subprocess

mcp = FastMCP("Docker MCP Server")  # Named server instance

@mcp.tool
def running_containers():
    """Tool:1 Show running Containers"""
    result = subprocess.run(
        ["docker", "ps", "-q"],
        capture_output=True,
        text=True
    )
    return result.stdout

@mcp.tool
def container_logs_by_name(container_name):
    """Tool:2 Show Logs of Containers"""
    result = subprocess.run(
        ["docker", "logs", "--tail", "10", container_name],
        capture_output=True,
        text=True
    )
    return result.stdout

if __name__ == "__main__":
    mcp.run()  # Blocks on stdio, waits for JSON-RPC requests
```

**Key Design Decisions:**
| Decision | Rationale |
|----------|-----------|
| `FastMCP` wrapper | Handles JSON-RPC framing, schema generation, stdio transport automatically |
| `@mcp.tool` decorator | Auto-generates MCP tool schema (name, description, inputSchema) from docstring + signature |
| `subprocess.run` | Executes actual Docker CLI |
| `capture_output=True, text=True` | Returns clean string stdout to LLM |
| `mcp.run()` | Starts stdio server loop |


---

#### **Component 2: MCP Client Agent — `04-agent_with_mcp.py`** (The Tool Consumer)

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
import asyncio


async def main():
    # Connect to MCP server via stdio
    client = MultiServerMCPClient(
        {
            "docker-mcp" : {
            "transport": "stdio",
            "command":"python3",
            "args":["mcp_server.py"]  # Spawns server as subprocess
            }

        }
    )
    tools = await client.get_tools()    # MCP tools discovered at runtime!

    llm = ChatOllama(     # Local LLM
    model="gemma4",
    temperature="0.8"
    )

    # Agent with dynamically discovered MCP tools
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
```

**Key Design Decisions:**
| Decision | Rationale |
|----------|-----------|
| `MultiServerMCPClient` | Manages stdio subprocess lifecycle + JSON-RPC communication |
| `"command": "python3", "args": ["mcp_server.py"]` | Spawns server as child process |
| `await client.get_tools()` | **Dynamic discovery** — calls `tools/list` at runtime, converts to LangChain tools |
| `create_agent(llm, tools)` | LangChain agent that can invoke any discovered tool |
| `agent.ainvoke()` | Async invocation — non-blocking, streams tool calls/responses |

**Agent Reasoning Flow:**
```
User: "how many containers are running"
    │
    ▼
LLM (gemma4) receives: system prompt + user message + tool schemas
    │
    ▼
LLM decides: "I need to call running_containers tool"
    │
    ▼
LangChain agent → MCP Client → stdio → MCP Server
    │
    ▼
Server executes: subprocess.run(["docker", "ps", "-q"])
    │
    ▼
Server returns: "abc123\ndef456\n" (container IDs)
    │
    ▼
MCP Client → LangChain Agent → LLM
    │
    ▼
LLM synthesizes: "2 containers are running (abc123, def456)"
    │
    ▼
Printed to user
```

---

### 🏆 RESULT: What Was Achieved

#### **Qualitative Outcomes**
- **Protocol Standardization**: Tools now speak MCP — compatible with Cursor, VS Code, Claude Desktop, any MCP client
- **Separation of Concerns**: Server owns *execution* (Docker CLI), Client owns *reasoning* (LLM)
- **Zero Hardcoding**: Agent discovers 2 tools at startup; add 10 more in server → agent uses them automatically
- **Security**: No shell injection — tools execute via structured JSON-RPC with validated schemas
- **Observability**: Every tool call visible in JSON-RPC logs (request → response)

#### **Technical Artifacts Delivered**
```
agentic-ai-concepts/
├── mcp_server.py        # MCP Server: 2 Docker tools via stdio JSON-RPC
├── agent_with_mcp.py    # MCP Client: Dynamic discovery + LangChain agent
└── agentic-ai-solution.md      # THIS FILE
```

