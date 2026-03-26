FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install fastapi uvicorn pydantic requests

CMD ["uvicorn", "my_env.server.my_env_environment:app", "--host", "0.0.0.0", "--port", "7860"]