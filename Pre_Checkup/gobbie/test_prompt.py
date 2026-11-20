
from gobbie_ai.daily_report_function import (
    build_updated_history,
    create_precheckup_prompt
)


history = ""

history = build_updated_history(
    history,
    "Pagi ini aku sakit kepala.",
    "2026-11-20"
)

history = build_updated_history(
    history,
    "Kepalaku masih sakit dan sekarang agak mual.",
    "2026-11-20"
)

history = build_updated_history(
    history,
    "Mual sudah tidak terasa, kepala masih sakit.",
    "2026-11-20"
)

history = build_updated_history(
    history,
    "Besoknya aku masih sakit kepala.",
    "2026-11-21"
)

latest_message = "Besoknya aku masih sakit kepala."

prompt = create_precheckup_prompt(
    user_message=latest_message,
    history=history,
    report_date="2026-11-21"
)

print("=" * 45)
print("PRE-CHECKUP PROMPT TEST")
print("=" * 45)

print("Prompt berhasil dibuat.")

print("\nPrompt type:")
print(type(prompt))

print("\nPrompt length:")
print(len(prompt), "characters")

# Validasi konten prompt
checks = {
    "Latest message included": latest_message in prompt,
    "History included": history in prompt,
    "Timeline instruction included": "urutan kemunculannya" in prompt,
    "No JSON instruction included": "bukan JSON" in prompt
}

print("\nVALIDATION:")

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

if all(checks.values()):
    print("\nALL CHECKS PASSED!")
