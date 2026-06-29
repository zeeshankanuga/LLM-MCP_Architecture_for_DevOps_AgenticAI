# Agentic AI System: (MCP Server & Client)

**Author:** Zeeshan Kanuga

Built by [Zeeshan Kanuga](https://github.com/zeeshankanuga)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/zeeshankanuga/)

---

### 🎯 The Problem Space

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