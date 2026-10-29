"""Synthetic MCP approval probe. This module has no mail integration."""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import anyio
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, ToolAnnotations

TOOL_NAME = "outlook_send_draft"
SCHEMA = {
    "type": "object",
    "properties": {
        "case_id": {"type": "string", "minLength": 1, "maxLength": 128},
        "revision": {"type": "integer", "minimum": 1},
        "subject": {"type": "string", "maxLength": 4096},
        "body": {"type": "string", "maxLength": 100000},
        "attachments": {
            "type": "array", "maxItems": 100,
            "items": {"type": "string", "maxLength": 1024},
        },
    },
    "required": ["case_id", "revision", "subject", "body", "attachments"],
    "additionalProperties": False,
}


def create_server(event_path: Path) -> Server:
    server = Server("outlook-approval-probe")

    @server.list_tools()
    async def list_tools():
        return [Tool(
            name=TOOL_NAME,
            description=(
                "SIMULATION ONLY. Record a synthetic draft execution locally. "
                "No mail is accessed or sent. Attachment names are labels only."
            ),
            inputSchema=SCHEMA,
            annotations=ToolAnnotations(
                readOnlyHint=False, destructiveHint=True,
                idempotentHint=False, openWorldHint=False,
            ),
        )]

    @server.call_tool()
    async def call_tool(name, arguments):
        if name != TOOL_NAME:
            raise ValueError("Unknown probe tool")
        # Input schema validation runs in the MCP SDK before this handler.
        canonical = json.dumps(arguments, sort_keys=True, ensure_ascii=False)
        event = {
            "event": "simulated_execution",
            "execution_id": str(uuid4()),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "arguments": arguments,
            "snapshot_hash": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        }
        event_path.parent.mkdir(parents=True, exist_ok=True)
        # No queue, retries, background tasks, or replay on startup.
        with event_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return [TextContent(type="text", text=json.dumps(event))]

    return server


async def serve(event_path: Path):
    server = create_server(event_path)
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    anyio.run(serve, parser.parse_args().events)
