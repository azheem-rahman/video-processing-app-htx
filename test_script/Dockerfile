FROM python:3.11-slim

WORKDIR /app

COPY test_workflow.py .
COPY SampleVideo_1280x720_1mb.mp4 .

RUN pip install --no-cache-dir requests

CMD [ "python", "test_workflow.py" ]