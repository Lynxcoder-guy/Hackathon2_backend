from dataclasses import asdict, dataclass, field

@dataclass
class DoctorNote:
    visit_id: str
    advice: str
    patient_name: str = ""
    patient_age: int = 0
    doctor_name: str = ""
    visit_date: str = ""
    diagnosis: str = ""
    prescriptions: list[str] = field(default_factory=list)
    follow_up: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "DoctorNote":
        return cls(**data)

    def to_dict(self) -> dict :
        return asdict(self)

    def to_text(self) -> str:
        prescriptions = "\n".join(f"   -  {p}" for p in self.prescriptions) or "  - none"
        lines = []
        if self.patient_name:
            lines.append(f"Nama Pasien:  {self.patient_name}")
        if self.patient_age > 0:
            lines.append(f"Umur:  {self.patient_age}")
        if self.doctor_name:
            lines.append(f"Dokter:  {self.doctor_name}")
        if self.diagnosis:
            lines.append(f"Diagnosis: {self.diagnosis}")
        lines.append(f"Doctor's Advice: {self.advice}")
        if self.prescriptions:
            lines.append(f"Prescription:\n{prescriptions}")
        if self.follow_up:
            lines.append(f"Follow up: {self.follow_up}")
        return "\n".join(lines)

@dataclass
class PlanTask:
    """One step of the actionable plan (can feed the habit planner / tracker)."""
    task_id:str
    title:str
    description:str
    frequency: str #sehari/setiap hari/seminggu

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class PostCheckUpReport:
    """Shown to the patient after the checkup"""
    note: DoctorNote
    ringkasan_simpel: str
    plan: list[PlanTask] = field(default_factory=list)
    ai_generated: bool = True

    def to_dict(self) -> dict:
        return {
            "patient_name": self.note.patient_name,
            "patient_age": self.note.patient_age,
            "ringkasan_simpel": self.ringkasan_simpel,
            "plan": [
                {
                    "title": task.title,
                    "description": task.description,
                    "frequency": task.frequency,
                }
                for task in self.plan
            ],
        }
    def to_text(self) -> str:
        plan = (
            "\n".join(
                f"- {task.title}: {task.description} ({task.frequency})"
                for task in self.plan
            )
            or "   (no task)"
        )
        return "\n".join(
            [
                f"Nama: {self.note.patient_name}",
                f"Umur: {self.note.patient_age}",
                "Ringkasan:",
                self.ringkasan_simpel,
                "Tindakan:",
                plan
            ]
        )