from pathlib import Path
import tempfile

import gobbie_ai.daily_report_function as daily


print("=" * 45)
print("REAL GEMINI AI TEST")
print("=" * 45)

# History temporary supaya data testing terisolasi
temp_dir = tempfile.TemporaryDirectory()

daily.HISTORY_FILE = (
    Path(temp_dir.name) / "real_ai_test.txt"
)

# Data dummy, bukan laporan kesehatan pribadi
test_message = (
    "Hari ini aku merasa lelah setelah aktivitas sekolah. "
    "Aku tidur sekitar 7 jam tadi malam."
)

test_date = "2026-11-20"

try:

    print("\nSending test report to Gemini...")

    result = daily.process_daily_report(
        user_message=test_message,
        report_date=test_date
    )

    print("\n" + "=" * 45)
    print("AI RESPONSE")
    print("=" * 45)

    print(result)

    print("\n" + "=" * 45)
    print("VALIDATION")
    print("=" * 45)

    print(
        "Output is String:",
        isinstance(result, str)
    )

    print(
        "Output is not empty:",
        bool(result.strip())
    )

    print(
        "History saved:",
        daily.HISTORY_FILE.exists()
    )

    if (
        isinstance(result, str)
        and result.strip()
        and daily.HISTORY_FILE.exists()
    ):
        print("\nREAL AI TEST PASSED!")

except Exception as error:

    print("\nREAL AI TEST FAILED!")
    print("Error type:", type(error).__name__)
    print("Error:", error)

finally:

    # Hapus history temporary setelah test
    temp_dir.cleanup()

    print("\nTemporary test history cleaned.")