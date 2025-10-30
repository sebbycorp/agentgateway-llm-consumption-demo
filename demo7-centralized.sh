#!/bin/bash

# Demo 7: Centralized Control

python3 -c "
import sys
sys.path.insert(0, '.')
from demo_complete import demo_centralized_control, print_section

print_section('Demo 7: Centralized Control')
demo_centralized_control()
"

