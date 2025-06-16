import asyncio
import logging
from fastmcp.client import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/sse"  # Ensure this matches your server's address

async def main():
    """Connects to the MCP server and tests a tool."""
    logger.info(f"Attempting to connect to MCP server at {SERVER_URL}")
    
    try:
        async with Client(SERVER_URL) as client:
            logger.info("Successfully connected to MCP server.")
            
            # 1. List available tools (optional, but good for verification)
            try:
                tools = await client.list_tools()
                logger.info(f"Available tools: {tools}")
                if not tools:
                    logger.warning("No tools reported by the server. Check server logs and structure.yaml.")
                    return
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return

            # 2. Define the tool name and parameters
            # This should match a tool defined in your books/structure.yaml
            tool_name = "search_book_knowledge" 
            
            if tool_name not in [tool.name for tool in tools]:
                logger.error(f"Tool '{tool_name}' not found in available tools. Ensure it's defined in structure.yaml and the server loaded it.")
                return

            # Example query - adapt as needed for your specific knowledge base
            # This query should be relevant to the content of your indexed PDFs
            # For the supplement therapy coach, this might be a health concern or a request for information.
            query_params = {
                "query": "What are the benefits of Vitamin D?",
            }
            
            logger.info(f"Calling tool '{tool_name}' with parameters: {query_params}")
            
            # 3. Call the tool
            try:
                response = await client.call_tool(tool_name, query_params)
                logger.info(f"Tool '{tool_name}' response:")
                # Pretty print the response if it's a dictionary or list
                if isinstance(response, (dict, list)):
                    import json
                    logger.info(json.dumps(response, indent=2, ensure_ascii=False))
                else:
                    logger.info(response)
            except Exception as e:
                logger.error(f"Error calling tool '{tool_name}': {e}", exc_info=True)
                
    except ConnectionRefusedError:
        logger.error(f"Connection refused. Ensure the MCP server is running at {SERVER_URL}.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
