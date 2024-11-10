from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    username: str
    password: str
    rossum_api_token: str
    rossum_api_url_template: str
    postbin_url: str


settings = Settings()
