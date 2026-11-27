class JSONFormatter:

    def group_by_patient(self, logs):

        if not isinstance(logs, list):
            raise ValueError("Logs harus berbentuk list.")

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
                grouped_data[patient_id] = []

            grouped_data[patient_id].append(log)

        return grouped_data

    def format_patient(self, grouped_data, patient_id):

        patient_id = str(patient_id)

        if patient_id not in grouped_data:
            raise ValueError(
                f"Patient ID {patient_id} tidak ditemukan."
            )

        logs = grouped_data[patient_id]

        # Susun log berdasarkan tanggal
        logs = sorted(
            logs,
            key=lambda log: log.get("date", "")
        )

        timeline = []

        for log in logs:

            date = log.get("date", "Tanggal tidak tersedia")
            report = log.get("report", "")

            if report:
                timeline.append(
                    f"Tanggal {date}: {report}"
                )

        # Format sebagai satu paragraf untuk input AI
        formatted_timeline = (
            f"Timeline laporan pasien {patient_id}: "
            + ". ".join(timeline)
            + "."
        )

        return formatted_timeline
