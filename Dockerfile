FROM python:3.11.3
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["run_server.py"]