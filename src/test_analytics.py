
from analytics import get_kpis

# Test with both transaction classes and all amounts
results = get_kpis(
    selected_classes=[0, 1],
    min_amount=0,
    max_amount=30000
)

print("\nSQL KPI RESULTS")
print("-------------------------")

for key, value in results.items():
    print(f"{key}: {value}")

from analytics import get_amount_segment_analysis

segment_results = get_amount_segment_analysis(
    min_amount=0,
    max_amount=30000
)

print("\nFRAUD RATE BY AMOUNT SEGMENT")
print("----------------------------")
print(segment_results)