#!/bin/bash

# Demo 2: PII Redaction & Data Security

python3 -c "
import sys
sys.path.insert(0, '.')
from demo_complete import demo_pii_redaction, print_section

print_section('Demo 2: PII Redaction & Data Security')
demo_pii_redaction()
"

