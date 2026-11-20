
import json

from gobbie_ai.log_reader import LogReader
from gobbie_ai.json_formatter import JSONFormatter
from gobbie_ai.precheckup_ai import PreCheckupAI
from gobbie_ai.precheckup_service import PreCheckupService


class PreCheckupTest:

    def __init__(self):

        self.log_reader = LogReader(
            "logs/patient_logs.json"
        )

        self.formatter = JSONFormatter()

        self.ai = PreCheckupAI()

    def run(self):

        print("=" * 45)
        print("GOBBIE PRE-CHECKUP TEST")
        print("=" * 45)

        service = PreCheckupService(
            self.log_reader,
            self.formatter,
            self.ai
        )

        result = service.run_precheckup("P001")

        print("\nPRE-CHECKUP RESULT:")
        print("=" * 45)

        print(
            json.dumps(
                result["summary"],
                indent=4,
                ensure_ascii=False
            )
        )

        print("\nOutput file:")
        print(result["output_file"])


if __name__ == "__main__":

    test = PreCheckupTest()
    test.run()
