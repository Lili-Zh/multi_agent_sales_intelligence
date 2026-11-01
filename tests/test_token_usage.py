
from crewai.crews.crew_output import CrewOutput


def inspect_token_usage():
    print("CrewOutput fields:")
    print(list(CrewOutput.model_fields.keys()))

    field = CrewOutput.model_fields.get("token_usage")

    if field is not None:
        print("\nToken usage field type:")
        print(field.annotation)
        print("\nToken usage field definition:")
        print(field)
    else:
        print("\nToken usage field not found")


from crewai.types.usage_metrics import UsageMetrics


def inspect_usage_metrics():
    print("\nUsageMetrics fields:")

    for name, field in UsageMetrics.model_fields.items():
        print(f"{name}: {field.annotation}")

if __name__ == "__main__":
    inspect_token_usage()
    inspect_usage_metrics()


