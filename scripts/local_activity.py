
import json
import subprocess
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

# Set this to your actual iCanFlySDK repository path.
REPO = Path("/Users/user01/Documents/iCan-SourceTree/iCanFlySDK")

# Use the author email already configured in your local .env.
env_file = Path(".env")
settings = {}
for line in env_file.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip()

author_email = settings["GITLAB_AUTHOR_EMAIL"].lower()

# Count commits reachable from Develop only.
today = date.today()
cutoff = today - timedelta(days=364)

result = subprocess.run(
    [
        "git", "-C", str(REPO),
        "log", "Develop",
        "--since=365 days ago",
        "--format=%aI%x09%ae",
    ],
    check=True,
    capture_output=True,
    text=True,
)

counts = Counter()

for line in result.stdout.splitlines():
    timestamp, email = line.split("\t", 1)
    if email.strip().lower() != author_email:
        continue

    commit_day = datetime.fromisoformat(timestamp).date()
    if cutoff <= commit_day <= today:
        counts[commit_day.isoformat()] += 1

# Explicit allowlist: only date strings and integer counts.
output = {
    "generated_on": today.isoformat(),
    "period_days": 365,
    "daily_commits": [
        {
            "date": (cutoff + timedelta(days=i)).isoformat(),
            "count": counts.get(
                (cutoff + timedelta(days=i)).isoformat(), 0
            ),
        }
        for i in range(365)
    ],
}

Path("activity.json").write_text(
    json.dumps(output, indent=2) + "\n",
    encoding="utf-8",
)

print("Activity report generated locally.")
print("Days included:", len(output["daily_commits"]))
print("Total matching commits:", sum(counts.values()))
print("Output contains dates and counts only.")

