#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Startup script started at $(date)"

# --- Environment Variables for .NET/Mono ---
export APP_DOMAIN_FRIENDLY_NAME="MyFastApiAdomdApp"
export PYTHONNET_RUNTIME="mono" # Explicitly set pythonnet to use Mono

# For more detailed Mono logging (can be very verbose, use for diagnostics only):
# export MONO_LOG_LEVEL="debug"
# export MONO_LOG_MASK="all" 
# More targeted Mono logging for assembly loading issues:
# export MONO_LOG_LEVEL="debug"
# export MONO_LOG_MASK="asm"

echo "Environment variables set:"
echo "APP_DOMAIN_FRIENDLY_NAME=${APP_DOMAIN_FRIENDLY_NAME}"
echo "PYTHONNET_RUNTIME=${PYTHONNET_RUNTIME}"
# if [ -n "$MONO_LOG_LEVEL" ]; then echo "MONO_LOG_LEVEL=${MONO_LOG_LEVEL}"; fi
# if [ -n "$MONO_LOG_MASK" ]; then echo "MONO_LOG_MASK=${MONO_LOG_MASK}"; fi

# --- System Package Installation ---
echo "Updating package lists..."
apt-get update -y
echo "Installing mono-runtime..."
apt-get install -y --no-install-recommends mono-runtime
echo "Mono runtime installation completed."

# Verify mono installation (optional but good for diagnostics)
if command -v mono &> /dev/null
then
    echo "Mono version:"
    mono --version
else
    echo "ERROR: Mono command not found after installation attempt."
    exit 1
fi

# --- Application Startup ---
# Navigate to the application directory if necessary (Azure App Service typically runs scripts from /home/site/wwwroot)
# cd /home/site/wwwroot

echo "Starting FastAPI development server..."
# Azure App Service sets the PORT environment variable.
# fastapi run will bind to 0.0.0.0 and the port specified by $PORT.
# If $PORT is not set, it defaults to 8000.
fastapi run main.py --host 0.0.0.0 --port ${PORT:-8000}

echo "Startup script finished at $(date)"

