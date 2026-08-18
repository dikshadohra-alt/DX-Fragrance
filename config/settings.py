import os


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dx-fragrance-development-secret-key"
    )

    DATABASE_PATH = os.path.join(
        "database",
        "dx_fragrance.db"
    )