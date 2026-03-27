from app.agent import agent_service
try:
    print("Testing agent...")
    answer = agent_service.run("Hello there!", session_id="test1234")
    print("Answer:", answer)
except Exception as e:
    import traceback
    traceback.print_exc()
