from mcp.server.fastmcp import FastMCP
from university_catalog.mcp.tools import register_tools
from university_catalog.mcp.resources import register_resources
from university_catalog.mcp.prompts import register_prompts


def create_mcp_server() -> FastMCP:
    mcp = FastMCP("University Course Catalog")
    
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    
    return mcp


mcp_server = create_mcp_server()