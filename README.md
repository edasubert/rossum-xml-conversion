# ROSSUM - Python Web application for XML conversion

## Build and Run

To successfully run the application, an `.env` file with secrets has to be provided, following the following template (add your own Rossum API url and token as well as a postbin url):

```
USERNAME=myUser123
PASSWORD=secretSecret
ROSSUM_API_URL_TEMPLATE=
ROSSUM_API_TOKEN=
POSTBIN_URL=
```

Then build and run the application using docker:

```
docker build -t xml_conversion .
docker run -it --name xml_conversion -p 8000:80 --env-file .env  xml_conversion
```
## Testing and Conventions
To run testing and conventions through poetry, install it first:
```
poetry install
```

### Testing
Tests are set up using pytest with coverage:
```
poetry run pytest --cov=xml_conversion --cov-report=term-missing tests
```

### Conventions
Several conventions are followed, namely black formatting, isort import sorting and mypy:
```
poetry run black --check xml_conversion tests 
poetry run isort --check xml_conversion tests 
poetry run mypy xml_conversion tests
```
