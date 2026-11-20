from pathlib import Path
import tempfile

import gobbie_ai.daily_report_function as daily


print("=" * 45)
print("OFFLINE INTEGRATION TEST")
print("=" * 45)

# 1. Gunakan file TXT sementara agar history asli aman
temp_dir = tempfile.TemporaryDirectory()

daily.HISTORY_FILE = (
    Path(temp_dir.name) / "test_history.txt"
)

# 2. Simulasikan AI tanpa request ke Gemini
def fake_ai(
    user_message: str,
    history: str,
    report_date: str
) -> str:

    # Pastikan prompt bisa dibuat
    prompt = daily.create_precheckup_prompt(
        user_message=user_message,
        history=history,
        report_date=report_date
    )

    assert user_message in prompt
    assert history in prompt
    assert report_date in prompt

    return (
        "GOBBIE PRE-CHECKUP\n\n"
        f"Tanggal laporan: {report_date}\n"
        "Keluhan yang dilaporkan: Data simulasi.\n"
        "Perkembangan keluhan: Tes offline berhasil.\n"
        "Timeline laporan: Laporan simulasi diterima.\n"
        "Informasi yang belum tersedia: Data kesehatan asli.\n"
        "Catatan: Ini merupakan hasil simulasi."
    )


# 3. Ganti AI asli dengan AI simulasi
daily.generate_precheckup = fake_ai


# 4. Test laporan pertama
result_1 = daily.process_daily_report(
    user_message="Hari ini saya merasa kurang fit.",
    report_date="2026-11-20"
)

print("\nTEST 1:")
print("Output type:", type(result_1))
print("Summary returned:", bool(result_1))


# 5. Test laporan kedua, tanggal yang sama
result_2 = daily.process_daily_report(
    user_message="Sekarang saya merasa lebih baik.",
    report_date="2026-11-20"
)

print("\nTEST 2:")
print("Same-day report accepted:", bool(result_2))


# 6. Test laporan pada hari berikutnya
result_3 = daily.process_daily_report(
    user_message="Hari berikutnya saya sudah kembali normal.",
    report_date="2026-11-21"
)

print("\nTEST 3:")
print("Next-day report accepted:", bool(result_3))


# 7. Periksa history yang tersimpan
saved_history = daily.read_history()

print("\nSAVED HISTORY:")
print(saved_history)


# 8. Validation
checks = {
    "First report returned String": isinstance(result_1, str),
    "Second report returned String": isinstance(result_2, str),
    "Third report returned String": isinstance(result_3, str),
    "First date exists": "[2026-11-20]" in saved_history,
    "Second date exists": "[2026-11-21]" in saved_history,
    "Same-day reports grouped": (
        saved_history.count("[2026-11-20]") == 1
    ),
    "First report saved": (
        "Hari ini saya merasa kurang fit."
        in saved_history
    ),
    "Second report saved": (
        "Sekarang saya merasa lebih baik."
        in saved_history
    ),
    "Next-day report saved": (
        "Hari berikutnya saya sudah kembali normal."
        in saved_history
    ),
    "AI simulation returned": (
        "Tes offline berhasil." in result_1
    )
}

print("\nVALIDATION:")

for name, passed in checks.items():
    print(
        f"{name}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

if all(checks.values()):
    print("\nALL INTEGRATION TESTS PASSED!")
else:
    print("\nSOME TESTS FAILED!")

# Bersihkan file temporary
temp_dir.cleanup()