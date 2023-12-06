from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    # database_port: str
    database_server:str
    database_name: str
    database_password: str
    database_username: str
    secret_key: str
    refresh_secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    class Config:
        env_file = ".env"



setting = Settings() # type: ignore