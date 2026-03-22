try:
    from backend.app import app
    print("Backend app imported successfully")
except Exception as e:
    print(f"Error importing backend app: {e}")
    import traceback
    traceback.print_exc()
