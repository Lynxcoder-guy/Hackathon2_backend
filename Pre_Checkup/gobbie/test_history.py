
from gobbie_ai.daily_report_function import build_updated_history


history = ""

# Hari pertama: laporan pagi
history = build_updated_history(
    history,
    "Pagi ini aku sakit kepala.",
    "2026-11-20"
)

# Hari pertama: laporan siang
history = build_updated_history(
    history,
    "Kepalaku masih sakit dan sekarang agak mual.",
    "2026-11-20"
)

# Hari pertama: laporan malam
history = build_updated_history(
    history,
    "Mual sudah tidak terasa, kepala masih sakit.",
    "2026-11-20"
)

# Hari kedua
history = build_updated_history(
    history,
    "Besoknya aku masih sakit kepala.",
    "2026-11-21"
)

# Tes duplicate
before_duplicate = history

history = build_updated_history(
    history,
    "Besoknya aku masih sakit kepala.",
    "2026-11-21"
)

print("=" * 40)
print("MULTI DAILY HISTORY TEST")
print("=" * 40)

print(history)

print("\nDuplicate check:")

print(
    "PASS"
    if history == before_duplicate
    else "FAIL"
)

print("\nOutput type:", type(history))
