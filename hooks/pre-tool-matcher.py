import json, sys

def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        tool = data.get(\ tool_name\, \\)
        if not tool or tool == \ skill\:
            query = str(data.get(\ tool_input\, {}))
            if \ github.com\ in query or \²Ö¿â\ in query:
                print(\ ÍÆ¼ö: mcp0_ask_question ²éÑ¯GitHub²Ö¿â\)
            if \ ËÑË÷\ in query or \²éÕÒ\ in query:
                print(\ ÍÆ¼ö: mcp1_web_search_exa ÓïÒåËÑË÷\)
    except:
        pass
    sys.exit(0)

if __name__ == \ __main__\:
    main()
