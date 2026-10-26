"""MCP stdio adapter over the same authenticated service used by the CLI."""

import json
import sys

from .client import call
from .registry import ResourceError

_TOOLS = {
    "search_resources": {"query": "string", "kind": "string", "language": "string", "task": "string", "modality": "string", "collection": "string", "configuration": "string", "split": "string", "streaming": "boolean", "max_size_bytes": "integer", "max_privacy_risk": "string", "operation": "string", "limit": "integer"},
    "list_collections": {},
    "get_resource": {"resource_id": "string"},
    "get_quick_start": {"resource_id": "string"},
    "preview_dataset": {"resource_id": "string", "limit": "integer"},
    "check_usage_rights": {"resource_id": "string", "operation": "string"},
    "compare_resources": {"resource_ids": "array", "operation": "string"},
    "get_resource_history": {"resource_id": "string"},
    "generate_manifest": {"resource_ids": "array", "project": "string", "operation": "string"},
    "submit_candidate": {"resource": "object"},
    "save_resource_manifest": {"manifest": "object"},
    "submit_evaluation": {"resource_id": "string", "finding": "object"},
}
_REQUIRED = {"get_resource": ["resource_id"], "get_quick_start": ["resource_id"], "preview_dataset": ["resource_id"], "check_usage_rights": ["resource_id", "operation"], "compare_resources": ["resource_ids"], "get_resource_history": ["resource_id"], "generate_manifest": ["resource_ids", "project", "operation"], "submit_candidate": ["resource"], "save_resource_manifest": ["manifest"], "submit_evaluation": ["resource_id", "finding"]}


def handle(message):
    method = message.get("method")
    ident = message.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": ident, "result": {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "kieu-resource", "version": "0.1.0"}}}
    if method == "tools/list":
        tools = []
        for name, fields in _TOOLS.items():
            tools.append({"name": name, "description": "Kieu Resources " + name.replace("_", " "), "inputSchema": {"type": "object", "properties": {key: {"type": kind} for key, kind in fields.items()}, "required": _REQUIRED.get(name, []), "additionalProperties": False}})
        return {"jsonrpc": "2.0", "id": ident, "result": {"tools": tools}}
    if method == "tools/call":
        params = message.get("params", {})
        name, args = params.get("name"), params.get("arguments", {})
        if name not in _TOOLS or not isinstance(args, dict):
            return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32602, "message": "unknown tool or invalid arguments"}}
        try:
            value = call(name, args)
            result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "structuredContent": {"value": value}}
        except ResourceError as exc:
            result = {"content": [{"type": "text", "text": json.dumps({"error": exc.as_dict()})}], "isError": True}
        return {"jsonrpc": "2.0", "id": ident, "result": result}
    return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": "method not found"}}


def main():
    for line in sys.stdin:
        try:
            reply = handle(json.loads(line))
        except (ValueError, TypeError) as exc:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if reply is not None:
            print(json.dumps(reply, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
