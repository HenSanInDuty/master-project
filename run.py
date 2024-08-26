import uvicorn 
from src.api import api
from streamlit.web import cli
import threading
import logging

def run_fastapi():
    logging.info("Starting server ....")
    uvicorn.run(api.app, host="0.0.0.0", port=8000, reload=True)
    
def run_streamlit():
    logging.info("Starting GUI ....")
    cli.main_run(["./src/gui/gui.py"])

if __name__ == "__main__":
    fastapi = threading.Thread(target=run_fastapi)
    fastapi.start()
    
    # Streamlit cannot run on another thread but main thread :'>
    run_streamlit()