FROM python:3.12 

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -
ENV PATH="/etc/poetry/bin:$PATH"

WORKDIR /code

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY tests tests
COPY xml_conversion xml_conversion

CMD ["poetry", "run", "uvicorn", "xml_conversion.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
