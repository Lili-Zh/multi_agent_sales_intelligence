
import json
import re
from pathlib import Path


def extract_overall_fit(strategy_text: str) -> str | None:
    """
    Extract account-level fit from the Overall Fit Assessment section.
    """
    section_match = re.search(
        r"^##\s+\d+\.\s+Overall Fit Assessment\s*$"
        r"(.*?)(?=^##\s+|\Z)",
        strategy_text,
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    if not section_match:
        return None

    section_text = section_match.group(1)

    fit_match = re.search(
        r"Overall fit:\s*\*{0,2}\s*"
        r"(INSUFFICIENT EVIDENCE|STRONG|MODERATE|WEAK)\b",
        section_text,
        flags=re.IGNORECASE,
    )

    if not fit_match:
        return None

    return fit_match.group(1).upper()


def run_golden_evaluation():
    dataset_path = Path("tests/golden_dataset.json")
    strategy_path = Path("sales_strategy_report.md")

    golden_dataset = json.loads(
        dataset_path.read_text(encoding="utf-8")
    )

    strategy_text = strategy_path.read_text(encoding="utf-8")

    print("Golden Dataset loaded successfully.")
    print(f"Total test cases: {len(golden_dataset['test_cases'])}")

    results = []
    for case in golden_dataset["test_cases"]:
        case_id = case["case_id"]
        company_name = case["company_name"]
        expected_fit = case["expected_fit"].upper()

        actual_fit = extract_overall_fit(strategy_text)

        print(f"\nTest Case: {case_id}")
        print(f"Company: {company_name}")
        print(f"Expected Fit: {expected_fit}")
        print(f"Actual Fit: {actual_fit}")

        if actual_fit is None:
            print("Result: ERROR - Could not extract overall fit")
        elif actual_fit == expected_fit:
            print("Result: PASS")
        else:
            print("Result: FAIL")

        
        if actual_fit is None:
            status = "ERROR"
        elif actual_fit == expected_fit:
            status = "PASS"
        else:
            status = "FAIL"

        results.append({
            "case_id": case_id,
            "company_name": company_name,
            "expected_fit": expected_fit,
            "actual_fit": actual_fit,
            "status": status,
        })

    
    output_path = Path("golden_evaluation.json")

    output_path.write_text(
        json.dumps(
            {"results": results},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nGolden evaluation saved to: {output_path}")


if __name__ == "__main__":
    run_golden_evaluation()
