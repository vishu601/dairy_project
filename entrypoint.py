import os
import subprocess

port = os.environ.get("PORT", "10000")
print(f"Starting server on port {port}")
subprocess.run(["gunicorn", "core.wsgi:application", "--bind", f"0.0.0.0:{port}"])