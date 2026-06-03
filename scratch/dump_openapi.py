import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from backend.__init__ import app

with open("scratch/openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)
print("OpenAPI schema dumped successfully.")
