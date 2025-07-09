# SSE Endpoint Documentation

This document provides comprehensive documentation for the Server-Sent Events (SSE) endpoint of the Blood Test MCP Server.

## Base URL

```
https://supplement-therapy.up.railway.app/sse
```

## Overview

The SSE endpoint provides a persistent, one-way connection for receiving real-time updates from the MCP server. It's particularly useful for:

- Receiving streaming responses from MCP tools
- Getting real-time updates on long-running operations
- Implementing interactive chat interfaces

## Authentication

Currently, the endpoint does not require authentication. However, in a production environment, you should secure this endpoint.

## Endpoints

### `GET /sse`

Establishes an SSE connection to receive events from the server.

**Headers:**
- `Accept: text/event-stream` (required)
- `Cache-Control: no-cache` (recommended)
- `Connection: keep-alive` (recommended)

**Query Parameters:**
- `tool`: (optional) The name of the tool to invoke
- `args`: (optional) JSON-encoded arguments for the tool

**Example Request:**
```http
GET /sse?tool=search_book_knowledge&args={"query":"Vitamin D benefits"} HTTP/1.1
Host: supplement-therapy.up.railway.app
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Example Response:**
```
event: connected
data: {"status": "connected", "timestamp": "2025-06-19T09:15:00Z"}

event: tool_response
data: {"result": "Vitamin D is essential for...", "metadata": {...}}

event: complete
data: {"status": "complete", "timestamp": "2025-06-19T09:15:02Z"}
```

### `POST /sse`

Establishes an SSE connection and sends a JSON-RPC request to invoke an MCP tool.

**Headers:**
- `Content-Type: application/json` (required)
- `Accept: text/event-stream` (required)
- `Cache-Control: no-cache` (recommended)
- `Connection: keep-alive` (recommended)

**Request Body:**
A JSON-RPC 2.0 request object:
```json
{
  "jsonrpc": "2.0",
  "method": "mcp.tool.invoke",
  "params": {
    "tool": "tool_name",
    "args": {
      "param1": "value1",
      "param2": "value2"
    }
  },
  "id": 1
}
```

**Example Request:**
```http
POST /sse HTTP/1.1
Host: supplement-therapy.up.railway.app
Content-Type: application/json
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

{
  "jsonrpc": "2.0",
  "method": "mcp.tool.invoke",
  "params": {
    "tool": "search_book_knowledge",
    "args": {
      "query": "What are the benefits of Vitamin D?"
    }
  },
  "id": 1
}
```

## Event Types

The following event types may be sent by the server:

- `connected`: Sent when the connection is established
- `tool_response`: Contains the result of a tool invocation
- `error`: Indicates an error occurred
- `complete`: Indicates the operation is complete
- `keepalive`: A keep-alive message to prevent timeouts

## Error Handling

Errors are sent as events with the `error` type. The data field contains an object with error details.

**Example Error:**
```
event: error
data: {"code": -32601, "message": "Method not found", "data": null}
```

## Client-Side Example

Here's how to connect to the SSE endpoint using JavaScript:

```javascript
const eventSource = new EventSource('https://supplement-therapy.up.railway.app/sse');

eventSource.onopen = () => {
  console.log('SSE connection established');};

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received data:', data);};

eventSource.addEventListener('tool_response', (event) => {
  const result = JSON.parse(event.data);
  console.log('Tool response:', result);});

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();};
```

## Rate Limiting

To ensure fair usage, the following rate limits apply:

- 60 requests per minute per IP address
- 1000 events per minute per connection

## Best Practices

1. Always implement reconnection logic in your client
2. Handle connection drops gracefully
3. Close connections when not needed
4. Use the `id` field to correlate requests and responses
5. Implement proper error handling

## Troubleshooting

- **Connection issues**: Verify the endpoint URL and CORS headers
- **No events received**: Check the network tab in developer tools
- **Unexpected disconnections**: Implement reconnection logic in your client
- **Authentication errors**: Ensure proper authentication headers are set

## Support

For issues or questions, please contact the development team or open an issue in the repository.
