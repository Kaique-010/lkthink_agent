FROM python:3.12-slim

WORKDIR /app

COPY dist/ /tmp/dist/

RUN python -m pip install --no-cache-dir \
    "/tmp/dist/lkthink_agent-0.1.0-py3-none-any.whl[postgres,api,knowledge,mcp]"

COPY docker/smoke_test.py /app/smoke_test.py

CMD ["python", "/app/smoke_test.py"]
