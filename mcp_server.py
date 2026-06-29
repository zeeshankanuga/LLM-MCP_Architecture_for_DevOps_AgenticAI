from fastmcp import FastMCP
import subprocess

mcp = FastMCP("Docker MCP Server")  # instance

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
    # run docker logs command
    """Tool:2 Show Logs of Containers"""
    result = subprocess.run(
        ["docker", "logs", "--tail", "10", container_name],
        capture_output=True,
        text=True
    )
    return result.stdout

if __name__ == "__main__":
    mcp.run()