#!/bin/bash
set -e

# Detect architecture (x86_64 or aarch64)
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    MAMBA_URL="https://micro.mamba.pm/api/micromamba/linux-64/latest"
elif [[ "$ARCH" == "aarch64" ]]; then
    MAMBA_URL="https://micro.mamba.pm/api/micromamba/linux-aarch64/latest"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

echo "Installing micromamba for $MAMBA_ARCH"

# Install micromamba for the detected arch
curl -Ls "$MAMBA_URL" | tar -xvj bin/micromamba
export PATH="$PWD/bin:$PATH"

# Initialize micromamba for this shell
eval "$(micromamba shell hook --shell bash)"

# Create environment and install SUNDIALS from conda-forge
micromamba create -f "environments/ci_environment.yml" -y
micromamba activate sun

# Export paths for build
export SUNDIALS_PREFIX="$CONDA_PREFIX"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

echo "SUNDIALS_PREFIX=$SUNDIALS_PREFIX"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
