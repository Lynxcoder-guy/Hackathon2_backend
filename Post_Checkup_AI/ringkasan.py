import json
import logging
import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .models import DoctorNote, PlanTask, PostCheckUpReport

load_dotenv(override=True)

logger = logging.getLogger(__name__)
default_model = "gemini-3.5-flash-lite"
ringkasan_error = (
    "Ringkasan belum tersedia. Silakan hubungi dokter atau klinik untuk mendapatkan penjelasan."
)


class TaskDraft(BaseModel):
    title: str = Field(description="Tugas atau short action seperti 'Take 2 Paracetamol'")
    description: str = Field(description="Kapan dan cara mengonsumsi obat, dengan kata simple")
    frequency: Literal["once", "daily", "weekly", "as needed"]


class ReportDraft(BaseModel):
    ringkasan_simpel: str = Field(
        description="Ringkasan untuk pasien dengan bahasa sehari-hari, 3-6 kalimat"
    )
    tasks: list[TaskDraft] = Field(
        description="Langkah konkret yang secara jelas disarankan di nota dokter"
    )


class GeminiClient:
    """Thin wrapper around the Gemini SDK that returns validated JSON."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        from google import genai

        load_dotenv(override=True)
        resolved_key = (api_key or os.getenv("GEMINI_API_KEY") or "").strip()
        if not resolved_key:
            raise RuntimeError("GEMINI_API_KEY Missing")

        self.model = (model or os.getenv("GEMINI_MODEL") or default_model).strip()
        self.client = genai.Client(api_key=resolved_key)


class PostCheckUpAI:
    """Turns a DoctorNote into a patient-friendly PostCheckUpReport using Gemini."""

    def __init__(self, note: DoctorNote):
        self.note = note
        try:
            self.client = GeminiClient()
            self.ai_available = True
        except RuntimeError:
            self.client = None
            self.ai_available = False

    def build_report(self) -> PostCheckUpReport:
        if not self.ai_available:
            return PostCheckUpReport(
                note=self.note,
                ringkasan_simpel=ringkasan_error,
                plan=[],
                ai_generated=False,
            )

        prompt = (
            "Buatlah ringkasan yang ramah pasien (bahasa Indonesia, 3-6 kalimat) "
            "dan rencana tindakan dari catatan dokter berikut.\n\n"
            f"Diagnosa: {self.note.diagnosis}\n"
            f"Saran dokter: {self.note.advice}\n"
            f"Resep: {', '.join(self.note.prescriptions) if self.note.prescriptions else 'Tidak ada'}\n"
            f"Follow-up: {self.note.follow_up if self.note.follow_up else 'Tidak ditentukan'}\n\n"
            "Balas dalam format JSON dengan kunci 'ringkasan_simpel' (string) dan "
            "'plan' (daftar objek dengan kunci 'title', 'description', 'frequency')."
        )

        try:
            response = self.client.client.models.generate_content(
                model=self.client.model,
                contents=prompt,
            )
            result = json.loads(response.text)
            ringkasan_simpel = result.get("ringkasan_simpel", ringkasan_error)
            plan = [
                PlanTask(
                    task_id=f"task_{i}",
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    frequency=item.get("frequency", ""),
                )
                for i, item in enumerate(result.get("plan", []))
            ]
            ai_generated = True
        except Exception:
            ringkasan_simpel = ringkasan_error
            plan = []
            ai_generated = False

        return PostCheckUpReport(
            note=self.note,
            ringkasan_simpel=ringkasan_simpel,
            plan=plan,
            ai_generated=ai_generated,
        )
