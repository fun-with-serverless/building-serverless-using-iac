#!/bin/bash

# Update system
sudo yum update -y

# Install prerequisites
sudo yum remove -y openssl-devel
sudo yum install -y gcc openssl11-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel wget curl git xz-devel

# Clone pyenv repository
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# Set up environment for pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile

# Apply changes to the current session
source ~/.bash_profile

# Install Python 3.11
pyenv install 3.11

# Install AWS SAM
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install
rm -rf aws-sam-cli-linux-x86_64.zip && rm -rf ./sam-installation
# Set Python 3.11 as global default
echo "Run 'source ~/.bash_profile && pyenv global 3.11' to complete the setup"