FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn pydantic requests

EXPOSE 7860

CMD ["uvicorn", "my_env.server.my_env_environment:app", "--host", "0.0.0.0", "--port", "7860"]
