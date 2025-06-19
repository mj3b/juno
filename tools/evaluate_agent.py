#!/usr/bin/env python3
"""
JUNO Agent Evaluation Tool

Evaluates JUNO's performance across different phases and use cases.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from juno.applications.evaluation_service.evaluator import JUNOEvaluator

def main():
    """Main evaluation entry point."""
    evaluator = JUNOEvaluator()
    
    print("🔍 Starting JUNO Evaluation...")
    results = evaluator.run_comprehensive_evaluation()
    
    print("\n📊 Evaluation Results:")
    for phase, metrics in results.items():
        print(f"  {phase}: {metrics}")
    
    return results

if __name__ == "__main__":
    main()

