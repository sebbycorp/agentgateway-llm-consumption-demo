#!/bin/bash

# Demo 1: Privacy & Data Leakage Prevention

python3 -c "
import sys
sys.path.insert(0, '.')
from demo_complete import demo_privacy_protection, print_section

print_section('Demo 1: Privacy & Data Leakage Prevention')
demo_privacy_protection()
"

