#!/usr/bin/env python3
"""
JUNO Report Generation Tool

Generates comprehensive reports and analytics.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from juno.applications.reporting_service.generator import ReportGenerator

def main():
    """Main report generation entry point."""
    generator = ReportGenerator()
    
    print("📊 Generating JUNO Reports...")
    reports = generator.generate_all_reports()
    
    print(f"✅ Generated {len(reports)} reports!")
    for report in reports:
        print(f"  - {report}")

if __name__ == "__main__":
    main()

