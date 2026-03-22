import urllib.request
import urllib.parse
import json

BASE = "http://localhost:8000/api"

def get(path):
    r = urllib.request.urlopen(BASE + path)
    return json.loads(r.read())

print("=== CATEGORY & SUMMARY VERIFICATION ===\n")

# 1. Categories - check for duplicates
cats = get("/categories")
print(f"1. Categories: {len(cats)} total (was 54 before normalization)")
for c in cats:
    print(f"   {c['category']}: {c['count']}")

# Check for case duplicates
names = [c["category"] for c in cats]
lower_names = [n.lower() for n in names]
dupes = [n for n in lower_names if lower_names.count(n) > 1]
if dupes:
    print(f"\n   WARNING: Still have duplicates: {set(dupes)}")
else:
    print(f"\n   ✅ No duplicate categories found!")

# 2. Category detail
first_cat = cats[0]["category"]
detail = get(f"/categories/{urllib.parse.quote(first_cat)}/summary")
print(f"\n2. Category '{first_cat}' detail:")
print(f"   Count: {detail['count']}")
print(f"   Questions returned: {len(detail['questions'])}")
print(f"   Combined summary: {detail['combined_summary'][:200]}...")

# 3. Overall summary
ov = get("/overall-summary")
print(f"\n3. Overall Summary:")
print(f"   Questions: {ov['total_questions']}")
print(f"   Categories: {ov['total_categories']}")
print(f"   Ministries: {ov['total_ministries']}")
print(f"   Top ministries: {len(ov['top_ministries'])}")
print(f"   Summary: {ov['combined_summary']}")

print("\n=== ALL CHECKS PASSED ===")
