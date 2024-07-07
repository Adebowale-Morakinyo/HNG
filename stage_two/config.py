import os

class Config:
    API_TITLE = "User Authentication & Organisation API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        f"postgresql://{os.getenv('PGUSER')}:{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('RAILWAY_TCP_PROXY_DOMAIN')}:{os.getenv('RAILWAY_TCP_PROXY_PORT')}/"
        f"{os.getenv('PGDATABASE')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
    PROPAGATE_EXCEPTIONS = True
