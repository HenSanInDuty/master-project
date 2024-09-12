FROM python:3.11-slim as api

# Install java 
RUN apt-get update && apt-get install -y default-jre

# Setup on api
COPY requirements_docker.txt api/requirements.txt
WORKDIR /api
RUN pip install -r requirements.txt
COPY . /api
EXPOSE 8000
CMD ["fastapi", "run", "src/api/api.py", "--host", "0.0.0.0", "--port", "8000" ,"--reload"]

# Seup on GUI
FROM python:3.11-slim as gui
COPY requirements_docker.txt gui/requirements.txt
WORKDIR /gui
RUN pip install -r requirements.txt
COPY . /gui
EXPOSE 8501
ENTRYPOINT ["streamlit","run"]
CMD ["src/gui/gui.py","--server.maxUploadSize","4086"]