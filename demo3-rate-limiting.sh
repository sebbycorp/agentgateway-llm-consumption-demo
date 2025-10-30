#!/bin/bash

# Demo 3: Rate Limiting

python3 -c "
import sys
sys.path.insert(0, '.')
from demo_complete import demo_rate_limiting, print_section

print_section('Demo 3: Rate Limiting')
demo_rate_limiting()
"

