FROM python:3.9

WORKDIR /code

ENV OPENAI_API_KEY=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

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
