#!/usr/bin/env python
"""Test agent tools creation."""

from agent.stock_agent import create_tools

print("Testing agent tools creation...")
tools = create_tools()
print(f"\n✅ Created {len(tools)} tools successfully!\n")

for i, tool in enumerate(tools, 1):
    print(f"  {i:2}. {tool.name}")

print("\n🎉 All tools registered successfully!")
