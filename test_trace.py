import sys
import time

def trace_import(name):
    print(f"DEBUG: Importing {name}...")
    start = time.time()
    try:
        __import__(name)
        print(f"DEBUG: {name} imported in {time.time() - start:.2f}s")
    except Exception as e:
        print(f"DEBUG: Error importing {name}: {e}")
        import traceback
        traceback.print_exc()

print("DEBUG: Starting trace")
trace_import("backend.database")
trace_import("backend.models")
trace_import("backend.auth")
trace_import("backend.chatbot")
trace_import("backend.chatbot.config")
trace_import("backend.chatbot.llm")
trace_import("backend.chatbot.retriever")
trace_import("backend.chatbot_api")
print("DEBUG: Trace finished")
