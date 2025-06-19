#!/usr/bin/env python3
"""
JUNO Memory Training Tool

Trains and optimizes JUNO's memory layer components.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from juno.core.memory.memory_layer import MemoryLayer

def main():
    """Main memory training entry point."""
    memory = MemoryLayer()
    
    print("🧠 Starting JUNO Memory Training...")
    memory.train_from_historical_data()
    
    print("✅ Memory training completed!")

if __name__ == "__main__":
    main()

