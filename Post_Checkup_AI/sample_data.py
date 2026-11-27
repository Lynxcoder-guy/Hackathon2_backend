"""Demo doctor notes so the AI can run before the real database exist."""

from .models import DoctorNote

SAMPLE_NOTES = {
    "V001":DoctorNote(
        visit_id="V001",
        patient_name="Lionel Messi",
        patient_age=39,
        doctor_name="Dr. Rahman",
        visit_date="2026-02-17",
        diagnosis="Stage 2 hypertension with hyperlipidemia; impaired fasting glucose.",
        advice=(
            "BP 152/96, LDL 165, FBS 118. Start antihypertensive and statin therapy. "
            "Low-sodium diet (<2 g sodium/day), reduce saturated fat. Aerobic exercise "
            "30 min, 5x/week. Smoking cessation strongly advised. Home BP monitoring "
            "every morning, record readings. Return immediately if chest pain, severe "
            "headache or shortness of breath."
        ),
        prescriptions=[
            "Amlodipine 5 mg, once daily in the morning",
            "Atorvastatin 20 mg, once daily at night."
        ],
        follow_up="Return in 4 weeks with BP log; repeat lipid panel and FBS in 3 months."
    ),
    "V002":DoctorNote(
        visit_id="V002",
        patient_name="Cristiano Ronaldo",
        patient_age=40,
        doctor_name="Dr. Sarah",
        visit_date="2026-11-06",
        diagnosis="Mild iron-deficiency anemia (Hb 11.2 g/dl)",
        advice=(
            "Continue oral iron; take with vitamin C source, avoid tea/coffee within"
            "1 hour of the dose. Increase dietary iron (red meat, spinach, legumes)."
        ),
        prescriptions=["Ferrous sulfate 325 mg, once daily after a meal"],
        follow_up="Repeat CBC in 8 weeks",
    ),
}