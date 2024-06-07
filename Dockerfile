FROM python:3.11.3
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod +x src/run_server.py
EXPOSE 8000
CMD ["python", "src/run_server.py"]