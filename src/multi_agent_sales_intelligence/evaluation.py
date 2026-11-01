import json
from pathlib import Path

from pydantic import ValidationError

from multi_agent_sales_intelligence.models import LeadResearchReport


def evaluate_research_report(report_path: str):
    """
    Load and validate a Lead Research Agent report.
    """

    path = Path(report_path)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        report = LeadResearchReport.model_validate(data)

        print("Research report loaded successfully.")
        print("Schema validation: PASS")
        print("Semantic validation: PASS")

        # Calculate Source URL Coverage        
        factual_evidence = [
            item for item in report.evidence
            if item.evidence_label in {"VERIFIED", "REPORTED"}
        ]

        evidence_with_url = [
            item for item in factual_evidence
            if item.source_url
        ]

        total = len(factual_evidence)
        with_url = len(evidence_with_url)

        coverage = (with_url / total * 100) if total > 0 else None

        print(f"Factual evidence records: {total}")
        print(f"Evidence records with URL: {with_url}")

        if coverage is not None:
            print(f"Source URL Coverage: {coverage:.1f}%")
        else:
            print("Source URL Coverage: N/A (no factual evidence)")

        # Calculate Primary Source Ratio
        primary_evidence = [
            item for item in factual_evidence
            if item.source_type == "PRIMARY"
        ]

        primary_count = len(primary_evidence)

        primary_ratio = (primary_count / total * 100) if total > 0 else None

        print(f"Primary source evidence records: {primary_count}")

        if primary_ratio is not None:
            print(f"Primary Source Ratio: {primary_ratio:.1f}%")
        else:
            print("Primary Source Ratio: N/A (no factual evidence)")

        # Calculate Evidence Label Distribution
        label_counts = {
            "VERIFIED": 0,
            "REPORTED": 0,
            "HYPOTHESIS": 0,
        }

        for item in report.evidence:
            label_counts[item.evidence_label] += 1

        print("\nEvidence Label Distribution:")
        print(f"VERIFIED: {label_counts['VERIFIED']}")
        print(f"REPORTED: {label_counts['REPORTED']}")
        print(f"HYPOTHESIS: {label_counts['HYPOTHESIS']}")

        evaluation_result = {
            "schema_valid": True,
            "semantic_valid": True,
            "total_evidence": len(report.evidence),
            "factual_evidence": total,
            "evidence_with_url": with_url,
            "source_url_coverage": coverage,
            "primary_source_count": primary_count,
            "primary_source_ratio": primary_ratio,
            "evidence_label_distribution": label_counts,
        }

        output_path = Path("research_evaluation.json")

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(evaluation_result, file, indent=2, ensure_ascii=False)

        print(f"\nEvaluation report saved to: {output_path}")

        return report

    except json.JSONDecodeError as e:
        print("JSON validation: FAIL")
        print(f"Error: {e}")
        return None

    except ValidationError as e:
        print("Schema or semantic validation: FAIL")
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    evaluate_research_report("lead_research_report.md")