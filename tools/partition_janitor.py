"""tools/partition_janitor.py — Track C2
Run monthly from n8n schedule trigger.

Creates next 3 months of hvac_call_log partitions ahead of time.
Optional: detach + archive partitions older than RETENTION_MONTHS to cold storage.
"""
import os, requests
from datetime import date
from dateutil.relativedelta import relativedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SRK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
LOOKAHEAD_MONTHS = int(os.environ.get("PARTITION_LOOKAHEAD", "3"))

def rpc(sql):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        headers={"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json"},
        json={"sql": sql},
    )
    print(sql, r.status_code)
    return r

def main():
    today = date.today().replace(day=1)
    for i in range(LOOKAHEAD_MONTHS + 1):
        target = today + relativedelta(months=i)
        # Use the helper installed by the C2 migration
        rpc(f"SELECT public.ensure_call_log_partition('{target.isoformat()}'::date);")

if __name__ == "__main__":
    main()
