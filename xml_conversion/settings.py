from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Defaults allows tests to run without setting the env variables,
    # the request will fail with username == None
    username: Optional[str] = None
    password: Optional[str] = None
    rossum_api_token: str = ""
    rossum_api_url_template: str = ""
    postbin_url: str = ""


settings = Settings()
