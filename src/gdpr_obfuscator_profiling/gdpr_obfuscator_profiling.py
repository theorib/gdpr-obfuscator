from cProfile import Profile
from pstats import SortKey, Stats
from timeit import timeit

from src.gdpr_obfuscator.core.gdpr_obfuscator import gdpr_obfuscator


def gdpr_obfuscator_profiling():
    aws_bucket = "test-bucket-c769a09"
    file_to_obfuscate = f"s3://{aws_bucket}/large_pii_data.csv"
    pii_fields = [
        "name",
        "email_address",
        "phone_number",
        "address",
    ]

    print("Starting profiling...")

    print("----Start timeit-----")

    iterations = 20

    total_time = timeit(
        lambda: gdpr_obfuscator(file_to_obfuscate, pii_fields), number=iterations
    )
    print(
        f"Total time average: {total_time / iterations} seconds (from {iterations} iterations)"
    )

    print("----End timeit-----")

    print("----Start cProfile-----")

    with Profile() as profile:
        gdpr_obfuscator(file_to_obfuscate, pii_fields)

    Stats(profile).strip_dirs().sort_stats(SortKey.CALLS).print_stats()

    print("----End cProfile-----")

    print("Profiling complete.")


if __name__ == "__main__":
    gdpr_obfuscator_profiling()
