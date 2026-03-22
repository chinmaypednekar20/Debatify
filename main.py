# ================= RUN FULL PIPELINE =================

from extractor.extractor import main as run_extractor
from summarizer.summarizer import main as run_summarizer


def main():

    print("\n==============================")
    print("🚀 FULL PARLIAMENT PIPELINE")
    print("==============================\n")

    # STEP 1 → Extract PDF
    print("🔹 STEP 1: EXTRACTION STARTING...\n")
    run_extractor()

    # STEP 2 → Summarize
    print("\n🔹 STEP 2: SUMMARIZATION STARTING...\n")
    run_summarizer()

    print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()