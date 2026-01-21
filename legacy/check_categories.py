import json

data = json.load(open('data.json', encoding='utf-8'))
iit_b = data[0]

print(f"College: {iit_b['university_name']}")
print(f"\nCourse Categories: {list(iit_b['courses_and_fees'].keys())}")
print(f"\nB.Tech courses: {len(iit_b['courses_and_fees']['B.Tech'])}")
print(f"M.Tech courses: {len(iit_b['courses_and_fees'].get('M.Tech', []))}")
print(f"Other Programs: {len(iit_b['courses_and_fees'].get('Other Programs', []))}")

print("\n--- Sample B.Tech Course ---")
print(json.dumps(iit_b['courses_and_fees']['B.Tech'][0], indent=2))
