from abc import ABC, abstractmethod
import logging
import datetime
from datetime import datetime, timezone
import json
import os


class BaseParser(ABC):
    PARSER_TYPE = None  # Should be defined in subclasses

    def __init__(self, cookies: dict, logger: logging.Logger):
        self.cookies = cookies
        self.logger = logger

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not hasattr(cls, "PARSER_TYPE"):
            raise NotImplementedError(
                "Subclasses of BaseParser must define a 'PARSER_TYPE' class attribute."
            )

    @abstractmethod
    def run(self):
        pass

    def create_result_filepath(self, error=False) -> str:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
        filename = f"{date}_{self.PARSER_TYPE}.json"
        if error:
            filename = f"error_{filename}"
        return os.path.join(
            BaseParser.results_directory_path(), f"{self.PARSER_TYPE}_results", filename
        )

    @staticmethod
    def results_directory_path() -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))

    def save_to_results(self, data, error=False):
        with open(self.create_result_filepath(error), "w") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write("\n")
