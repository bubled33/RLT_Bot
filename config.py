import tomllib
from pathlib import Path


class Config:
    def __init__(self, file_path: str | Path):
        with open(file_path, "rb") as file:
            file_data = tomllib.load(file)
        self._config_data = file_data

    def __getitem__(self, item):
        return self._config_data[item]
