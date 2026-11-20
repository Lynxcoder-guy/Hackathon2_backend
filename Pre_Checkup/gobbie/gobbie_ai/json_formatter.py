
class JSONFormatter:

    def group_by_patient(self, logs):

        if not isinstance(logs, list):
            raise ValueError(
                "Logs harus berbentuk list."
            )

        grouped_data = {}

        for index, log in enumerate(logs):

            if not isinstance(log, dict):
                raise ValueError(
                    f"Log ke-{index + 1} bukan object."
                )

            patient_id = log.get("patient_id")

            if not patient_id:
                raise ValueError(
                    f"Log ke-{index + 1} tidak memiliki patient_id."
                )

            patient_id = str(patient_id)

            if patient_id not in grouped_data:

                grouped_data[patient_id] = {
                    "patient_id": patient_id,
                    "logs": []
                }

            grouped_data[patient_id]["logs"].append(log)

        print(
            f"[JSON FORMATTER] Grouped {len(logs)} logs "
            f"into {len(grouped_data)} patients."
        )

        return grouped_data

    def format_patient(self, grouped_data, patient_id):

        patient_id = str(patient_id)

        if patient_id not in grouped_data:
            raise ValueError(
                f"Patient ID {patient_id} tidak ditemukan."
            )

        patient_data = grouped_data[patient_id]

        return patient_data
