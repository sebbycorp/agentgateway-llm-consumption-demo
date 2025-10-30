#!/bin/bash

# Demo 6: Multi-Provider Strategy

python3 -c "
import sys
sys.path.insert(0, '.')
from demo_complete import demo_multi_provider, print_section

print_section('Demo 6: Multi-Provider Strategy')
demo_multi_provider()
"

