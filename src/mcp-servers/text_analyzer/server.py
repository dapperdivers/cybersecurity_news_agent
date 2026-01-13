#!/usr/bin/env python3
"""
Text Analyzer MCP Server
Provides text summarization and analysis tools using Claude API
"""

import json
import sys
import os
from typing import Dict, Any


def summarize_text(text: str, style: str = "concise", max_points: int = 5) -> Dict[str, Any]:
    """
    Summarize text content

    Args:
        text: The text to summarize
        style: Summary style - "concise" (bullet points) or "paragraph" (prose)
        max_points: Maximum number of bullet points for concise style

    Returns:
        Dictionary with summary and metadata
    """
    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {
            "error": "ANTHROPIC_API_KEY environment variable not set"
        }

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        # Build prompt based on style
        if style == "concise":
            prompt = f"""Summarize the following text in {max_points} or fewer concise bullet points.
Focus on key facts, threats, impacts, and actionable information.

Text to summarize:
{text}

Provide the summary as a bullet point list."""

        else:  # paragraph style
            prompt = f"""Provide a concise paragraph summarizing the following text.
Focus on the main points, key threats, and important details.

Text to summarize:
{text}

Provide a single paragraph summary."""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        summary = message.content[0].text

        return {
            "summary": summary,
            "style": style,
            "original_length": len(text),
            "summary_length": len(summary)
        }

    except ImportError:
        return {
            "error": "anthropic package not installed. Run: pip install anthropic"
        }
    except Exception as e:
        return {
            "error": f"Error calling Claude API: {str(e)}"
        }


def extract_key_points(text: str, num_points: int = 5) -> Dict[str, Any]:
    """
    Extract key points from security content

    Args:
        text: The text to analyze
        num_points: Number of key points to extract

    Returns:
        Dictionary with key points and analysis
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {
            "error": "ANTHROPIC_API_KEY environment variable not set"
        }

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Analyze this cybersecurity content and extract the {num_points} most important key points.
For each point, identify:
- The key fact or finding
- Threat level (if applicable): Critical, High, Medium, Low, Info
- Affected systems/vendors (if mentioned)

Text to analyze:
{text}

Format as a numbered list with clear, actionable points."""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        key_points = message.content[0].text

        return {
            "key_points": key_points,
            "num_points_requested": num_points
        }

    except ImportError:
        return {
            "error": "anthropic package not installed. Run: pip install anthropic"
        }
    except Exception as e:
        return {
            "error": f"Error calling Claude API: {str(e)}"
        }


def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool calls"""

    if tool_name == "summarize_text":
        text = arguments.get('text')
        if not text:
            return {"error": "No text provided"}

        style = arguments.get('style', 'concise')
        max_points = arguments.get('max_points', 5)

        return summarize_text(text, style, max_points)

    elif tool_name == "extract_key_points":
        text = arguments.get('text')
        if not text:
            return {"error": "No text provided"}

        num_points = arguments.get('num_points', 5)

        return extract_key_points(text, num_points)

    else:
        return {"error": f"Unknown tool: {tool_name}"}


def main():
    """MCP Server main loop - stdio protocol"""

    # Tools definition
    tools = [
        {
            "name": "summarize_text",
            "description": "Summarize text content in concise bullet points or paragraph form",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to summarize"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["concise", "paragraph"],
                        "description": "Summary style - 'concise' for bullet points or 'paragraph' for prose (default: concise)"
                    },
                    "max_points": {
                        "type": "integer",
                        "description": "Maximum number of bullet points for concise style (default: 5)"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "extract_key_points",
            "description": "Extract and analyze key points from cybersecurity content",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze"
                    },
                    "num_points": {
                        "type": "integer",
                        "description": "Number of key points to extract (default: 5)"
                    }
                },
                "required": ["text"]
            }
        }
    ]

    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())

            if request.get('method') == 'initialize':
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "text_analyzer",
                            "version": "1.0.0"
                        }
                    }
                }

            elif request.get('method') == 'tools/list':
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "tools": tools
                    }
                }

            elif request.get('method') == 'tools/call':
                params = request.get('params', {})
                tool_name = params.get('name')
                arguments = params.get('arguments', {})

                result = handle_tool_call(tool_name, arguments)

                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": result
                }

            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "error": {"code": -32601, "message": "Method not found"}
                }

            print(json.dumps(response), flush=True)

        except Exception as e:
            print(f"Error processing request: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    main()
