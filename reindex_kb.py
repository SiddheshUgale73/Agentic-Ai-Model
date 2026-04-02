import os
import sys

# Ensure we can import from app
sys.path.append(os.path.abspath("."))

from app.services import rag_pipeline

def reindex():
    file_path = "data/uploads/institute_info.txt"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    
    print(f"Indexing {file_path}...")
    try:
        rag_pipeline.process_file(file_path)
        print("Success! Knowledge base updated.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    reindex()
