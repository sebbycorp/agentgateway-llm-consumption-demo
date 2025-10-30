#!/bin/bash

# Demo 5: Cost Tracking & Chargeback

python3 -c "
import sys
sys.path.insert(0, '.')
from demo_complete import demo_cost_tracking, print_section

print_section('Demo 5: Cost Tracking & Chargeback')
demo_cost_tracking()
"

