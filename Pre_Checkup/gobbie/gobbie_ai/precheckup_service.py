
import json
from pathlib import Path
from datetime import datetime, timezone


class PreCheckupService:

    def __init__(self, log_reader, formatter, ai):

        self.log_reader = log_reader
        self.formatter = formatter
        self.ai = ai

        self.output_folder = (
            Path(__file__).resolve().parent.parent
            / "output"
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def get_patient_data(self, patient_id):

        logs = self.log_reader.read_logs()

        grouped_data = self.formatter.group_by_patient(
            logs
        )

        patient_data = self.formatter.format_patient(
            grouped_data,
            patient_id
        )

        return patient_data

    def generate_summary(self, patient_data):

        print("[PRE-CHECKUP] Generating summary...")

        summary = self.ai.generate_summary(
            patient_data
        )

        summary["patient_id"] = patient_data["patient_id"]

        summary["generated_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        return summary

    def save_summary(self, summary):

        patient_id = summary["patient_id"]

        filename = (
            self.output_folder
            / f"precheckup_{patient_id}.json"
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                summary,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"[PRE-CHECKUP] Saved: {filename}"
        )

        return str(filename)

    def run_precheckup(self, patient_id):

        patient_data = self.get_patient_data(
            patient_id
        )

        summary = self.generate_summary(
            patient_data
        )

        output_file = self.save_summary(
            summary
        )

        return {
            "success": True,
            "summary": summary,
            "output_file": output_file
        }
