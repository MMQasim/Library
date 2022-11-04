from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    static_directory: str

    class Config:
        env_file = ".env"


settings = Settings()

# "postgresql://"+settings.database_name+":"+settings.database_password+"@"+settings.database_hostname+":"+settings.database_port+"/"+settings.database_name
