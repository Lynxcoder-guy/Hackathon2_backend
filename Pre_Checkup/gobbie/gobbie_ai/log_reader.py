
import json
from pathlib import Path


class LogReader:

    def __init__(self, log_file):

        self.log_file = Path(log_file)

    def read_logs(self):

        if not self.log_file.exists():
            raise FileNotFoundError(
                f"Log file tidak ditemukan: {self.log_file}"
            )

        try:
            with open(
                self.log_file,
                "r",
                encoding="utf-8"
            ) as file:

                logs = json.load(file)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Format JSON tidak valid: {error}"
            )

        if not isinstance(logs, list):
            raise ValueError(
                "Log harus berbentuk JSON Array."
            )

        for index, log in enumerate(logs):

            if not isinstance(log, dict):
                raise ValueError(
                    f"Log ke-{index + 1} harus berbentuk object."
                )

        print(
            f"[LOG READER] Successfully loaded {len(logs)} logs."
        )

        return logs
