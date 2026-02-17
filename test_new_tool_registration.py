"""
Test script to verify the new tool is properly registered in the agent.
"""

print("Testing Agent Tool Registration...")
print("=" * 70)

try:
    from agent.stock_agent import create_tools
    
    # Get all tools
    tools = create_tools()
    
    print(f"✅ Total tools registered: {len(tools)}\n")
    
    # List all tools
    print("Registered Tools:")
    print("-" * 70)
    
    for i, tool in enumerate(tools, 1):
        print(f"{i:2}. {tool.name}")
    
    print("\n" + "=" * 70)
    
    # Check if new tools are present
    tool_names = [t.name for t in tools]
    
    new_tools = [
        "detect_imminent_stockout_risk",
        "get_pending_order_summary"
    ]
    
    print("\nChecking New Tools (2026-02-08):")
    print("-" * 70)
    
    all_present = True
    for tool_name in new_tools:
        if tool_name in tool_names:
            tool = next(t for t in tools if t.name == tool_name)
            print(f"✅ {tool_name}")
            print(f"   Description: {tool.description[:100]}...")
        else:
            print(f"❌ {tool_name} - NOT FOUND!")
            all_present = False
    
    print("\n" + "=" * 70)
    
    if all_present:
        print("✅ ALL NEW TOOLS PROPERLY REGISTERED!")
        print("\nThe agent should now respond to questions like:")
        print("  - 'Quais produtos têm risco de ficar sem estoque?'")
        print("  - 'Me mostre produtos que vão zerar em breve'")
        print("  - 'Há produtos sem pedido de compra?'")
        print("  - 'Quais pedidos estão pendentes?'")
    else:
        print("❌ SOME TOOLS ARE MISSING!")
        exit(1)
    
    print("=" * 70)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
