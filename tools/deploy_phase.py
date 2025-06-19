#!/usr/bin/env python3
"""
JUNO Phase Deployment Tool

Deploys specific JUNO phases to production environments.
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from juno.infrastructure.deployment.production_orchestrator import ProductionOrchestrator

def main():
    """Main deployment entry point."""
    parser = argparse.ArgumentParser(description='Deploy JUNO Phase')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3, 4], required=True,
                       help='Phase number to deploy (1-4)')
    parser.add_argument('--environment', choices=['staging', 'production'], default='staging',
                       help='Target environment')
    
    args = parser.parse_args()
    
    orchestrator = ProductionOrchestrator()
    
    print(f"🚀 Deploying JUNO Phase {args.phase} to {args.environment}...")
    result = orchestrator.deploy_phase(args.phase, args.environment)
    
    if result:
        print("✅ Deployment successful!")
    else:
        print("❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

