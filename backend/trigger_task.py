#!/usr/bin/env python
from tasks import send_doctor_monthly_report

result = send_doctor_monthly_report.apply_async(args=[1, 2025, 11])
print(f"[OK] Task triggered with ID: {result.id}")
