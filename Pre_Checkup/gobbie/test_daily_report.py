
from gobbie_ai.daily_report_function import process_daily_report


def main():

    print("=" * 45)
    print("GOBBIE DAILY REPORT TEST")
    print("=" * 45)

    # Simulasi pesan user
    user_message = (
        "Hari ini aku masih sakit kepala, "
        "tapi udah nggak terlalu lelah."
    )

    result = process_daily_report(
        user_message=user_message,
        report_date="2026-11-21"
    )

    print("\nPRE-CHECKUP RESULT:")
    print("=" * 45)

    # Output berupa String
    print(result)

    print("\nOutput type:")
    print(type(result))


if __name__ == "__main__":
    main()
