import os


def get_and_assert_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable {name} not set")
    return value
