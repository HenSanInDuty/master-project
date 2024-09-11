FROM python:3.11 as api
COPY requirements_docker.txt api/requirements.txt
WORKDIR /api
RUN pip install -r requirements.txt
COPY . /api
EXPOSE 8000
CMD ["uvicorn", "src/api/api:app", "--host", "0.0.0.0", "--port", "8000" ,"--reload"]

FROM python:3.11 as gui
COPY requirements_docker.txt gui/requirements.txt
WORKDIR /gui
RUN pip install -r requirements.txt
COPY . /gui
EXPOSE 8501
ENTRYPOINT ["streamlit","run"]
CMD ["src/gui/gui.py --server.maxUploadSize 200"]