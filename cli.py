#!/usr/bin/env python
"""
Simple CLI for OpsAgent.
Usage:
    python cli.py --title "High CPU" --description "CPU > 90%" --source prometheus --labels severity=high,category=infrastructure
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.ops_agent import run_ops_agent

def main():
    parser = argparse.ArgumentParser(description="Run OpsAgent on an alert")
    parser.add_argument("--title", required=True, help="Alert title")
    parser.add_argument("--description", required=True, help="Alert description")
    parser.add_argument("--source", default="unknown", help="Alert source")
    parser.add_argument("--labels", default="", help="Comma-separated key=value pairs, e.g. severity=high,category=infrastructure")
    parser.add_argument("--value", type=float, default=None, help="Numeric value if applicable")
    args = parser.parse_args()

    labels = {}
    if args.labels:
        for pair in args.labels.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                labels[k.strip()] = v.strip()

    alert = {
        "title": args.title,
        "description": args.description,
        "source": args.source,
        "labels": labels,
    }
    if args.value is not None:
        alert["value"] = args.value

    # Optionally check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "dummy":
        print("Warning: OPENAI_API_KEY not set or set to 'dummy'. Using mock LLM.", file=sys.stderr)

    result = run_ops_agent(alert)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()