
import os
import json

from google import genai
from google.genai import types


class PreCheckupAI:

    def __init__(self, model="gemini-3.5-flash-lite"):


        self.model = model

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY belum diatur."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def create_prompt(self, patient_data):

        prompt = f"""
Kamu adalah Gobbie PRE-CHECKUP AI.

Tugas:
Membuat ringkasan laporan kesehatan berdasarkan
seluruh log yang dimasukkan oleh pasien.

DATA PASIEN:
{json.dumps(patient_data, ensure_ascii=False, indent=2)}

FORMAT OUTPUT WAJIB JSON:

{{
    "patient_id": "",
    "generated_at": "",
    "summary": {{
        "main_complaint": "",
        "symptoms": [],
        "symptom_duration": "",
        "symptom_frequency": "",
        "sleep_pattern": "",
        "energy_level": "",
        "mood": "",
        "physical_activity": "",
        "weekly_patterns": "",
        "additional_notes": ""
    }},
    "doctor_attention": [],
    "missing_information": [],
    "disclaimer": "Ringkasan berdasarkan laporan pasien, bukan diagnosis medis."
}}

ATURAN:
- Gunakan bahasa Indonesia profesional.
- Jangan memberikan diagnosis.
- Jangan memberikan resep atau pengobatan.
- Jangan mengarang informasi.
- Gunakan hanya informasi dari data pasien.
- Informasi yang tidak tersedia harus ditandai.
- Bedakan laporan pasien dan hal yang perlu diklarifikasi dokter.
- Perhatikan perubahan informasi dari beberapa log.
- Jangan menganggap perubahan sebagai pola jangka panjang
  jika data belum mencukupi.
- Hasil harus berupa JSON valid.
- Jangan menambahkan Markdown atau teks di luar JSON.
"""

        return prompt

    def generate_summary(self, patient_data):

        if not isinstance(patient_data, dict):
            raise ValueError(
                "Data pasien harus berbentuk dictionary."
            )

        if not patient_data:
            raise ValueError(
                "Data pasien kosong."
            )

        prompt = self.create_prompt(patient_data)

        print("[AI] Sending request to Gemini...")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=3000,
                response_mime_type="application/json"
            )
        )

        if not response.text:
            raise ValueError(
                "Gemini tidak menghasilkan ringkasan."
            )

        try:
            result = json.loads(response.text)

        except json.JSONDecodeError as error:

            print(
                "[AI ERROR] Gemini returned invalid JSON."
            )

            print(
                "[AI ERROR] Response length:",
                len(response.text)
            )

            raise ValueError(
                "Gemini menghasilkan JSON yang tidak valid."
            ) from error

        if not isinstance(result, dict):
            raise ValueError(
                "Format JSON Gemini tidak valid."
            )

        summary_fields = {
            "main_complaint": str,
            "symptoms": list,
            "symptom_duration": str,
            "symptom_frequency": str,
            "sleep_pattern": str,
            "energy_level": str,
            "mood": str,
            "physical_activity": str,
            "weekly_patterns": str,
            "additional_notes": str,
        }
        summary = result.get("summary")
        if not isinstance(summary, dict) or any(
            not isinstance(summary.get(field), expected_type)
            for field, expected_type in summary_fields.items()
        ):
            raise ValueError(
                "Gemini menghasilkan struktur summary yang tidak valid."
            )

        if (
            any(
                not isinstance(result.get(field), list)
                or not all(isinstance(item, str) for item in result[field])
                for field in ("doctor_attention", "missing_information")
            )
            or not all(isinstance(item, str) for item in summary["symptoms"])
            or not isinstance(result.get("disclaimer"), str)
        ):
            raise ValueError(
                "Gemini menghasilkan format ringkasan yang tidak valid."
            )

        result["patient_id"] = patient_data["patient_id"]

        print("[AI] Summary generated successfully.")

        return result
