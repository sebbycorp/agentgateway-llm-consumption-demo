#!/bin/bash

# Demo 4: Budget Enforcement

python3 -c "
import sys
sys.path.insert(0, '.')
from demo_complete import demo_budget_enforcement, print_section

print_section('Demo 4: Budget Enforcement')
demo_budget_enforcement()
"

