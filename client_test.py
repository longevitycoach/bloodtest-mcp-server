import asyncio
import logging
import json
from mcp.types import TextContent
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
                
                logger.info(f"Raw response object type: {type(response)}")

                parsed_data = None
                if isinstance(response, list) and len(response) > 0 and isinstance(response[0], TextContent):
                    logger.info(f"Received TextContent: {str(response[0])[:200]}...")
                    try:
                        parsed_data = json.loads(response[0].text)
                        logger.info("Successfully parsed JSON from TextContent.")
                    except json.JSONDecodeError as je:
                        logger.error(f"Failed to parse JSON from TextContent: {je}")
                        logger.error(f"TextContent data: {response[0].text}")
                else:
                    logger.warning(f"Unexpected response structure: {type(response)}. Expected list with TextContent.")

                if parsed_data and isinstance(parsed_data, dict):
                    if 'results' in parsed_data: # Specific handling for RAG output
                        logger.info(f"  Query: {parsed_data.get('query')}")
                        logger.info(f"  Number of results: {parsed_data.get('results_count')}")
                        for i, res_item in enumerate(parsed_data.get('results', [])):
                            logger.info(f"  --- Result {i+1} ---")
                            logger.info(f"    Type: {type(res_item)}")
                            content = res_item.get('content', str(res_item)) if isinstance(res_item, dict) else str(res_item)
                            metadata = res_item.get('metadata', {}) if isinstance(res_item, dict) else {}
                            score = res_item.get('similarity_score', 'N/A') if isinstance(res_item, dict) else 'N/A'
                            
                            logger.info(f"    Content (snippet): {content[:200]}{'...' if len(content) > 200 else ''}")
                            logger.info(f"    Metadata: {metadata}")
                            logger.info(f"    Score: {score}")
                    else:
                        # Generic dictionary printing for other successful JSON parses
                        logger.info("  Parsed JSON (dictionary details):")
                        for key, value in parsed_data.items():
                            logger.info(f"    {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
                elif parsed_data: # If parsed_data is not a dict but something else (e.g. list from JSON)
                    logger.info(f"  Parsed JSON (type: {type(parsed_data)}, snippet): {str(parsed_data)[:500]}{'...' if len(str(parsed_data)) > 500 else ''}")

            except Exception as e:
                logger.error(f"Error calling tool '{tool_name}' or processing its response: {e}", exc_info=True)
                
    except ConnectionRefusedError:
        logger.error(f"Connection refused. Ensure the MCP server is running at {SERVER_URL}.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
