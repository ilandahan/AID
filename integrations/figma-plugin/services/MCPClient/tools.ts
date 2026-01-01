/**
 * @file services/MCPClient/tools.ts
 * @description Tool and resource operations for MCP Client
 */

import type { MCPResponse } from '../../types';

type SendRequestFn = (method: string, params: unknown) => Promise<MCPResponse>;

/**
 * Call an MCP tool
 */
export async function callTool(
  name: string,
  args: Record<string, unknown>,
  send: SendRequestFn
): Promise<unknown> {
  const response = await send('tools/call', {
    name,
    arguments: args,
  });

  if (response.error) {
    throw new Error(response.error.message);
  }

  return response.result;
}

/**
 * List available tools
 */
export async function listTools(
  send: SendRequestFn
): Promise<Array<{
  name: string;
  description: string;
  inputSchema: unknown;
}>> {
  const response = await send('tools/list', {});

  if (response.error) {
    throw new Error(response.error.message);
  }

  type ToolDefinition = { name: string; description: string; inputSchema: unknown };
  const result = response.result as { tools: Array<ToolDefinition> };
  return (result && result.tools) ? result.tools : [];
}

/**
 * Get a resource from the server
 */
export async function getResource(
  uri: string,
  send: SendRequestFn
): Promise<unknown> {
  const response = await send('resources/read', { uri });

  if (response.error) {
    throw new Error(response.error.message);
  }

  return response.result;
}

/**
 * List available resources
 */
export async function listResources(
  send: SendRequestFn
): Promise<Array<{
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
}>> {
  const response = await send('resources/list', {});

  if (response.error) {
    throw new Error(response.error.message);
  }

  type ResourceDefinition = { uri: string; name: string; description?: string; mimeType?: string };
  const result = response.result as { resources: Array<ResourceDefinition> };
  return (result && result.resources) ? result.resources : [];
}
