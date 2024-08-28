# Use the official Ubuntu base image
FROM ubuntu:latest

# Set the environment variable to suppress prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV HOME="/root"

# Update the package list and install Python, Python venv, Git, and Curl
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    git \
    wget \
    tar \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    yq

RUN curl -sL https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -o /usr/bin/yq && chmod +x /usr/bin/yq

# Install Rust using the official installation script
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="$HOME/.cargo/bin:$PATH"

RUN cargo install aiken --version 1.0.29-alpha
RUN cargo install oura --version 1.9.0 --all-features 

# Download and extract Cardano Node
RUN wget https://github.com/IntersectMBO/cardano-node/releases/download/9.1.0/cardano-node-9.1.0-linux.tar.gz && \
    tar -zxvf cardano-node-9.1.0-linux.tar.gz -C /root

# Add cardano-cli to PATH
ENV PATH="/root/bin:$PATH"

# Set the working directory
WORKDIR /root/newm-batcher

# Copy the current directory contents into the container at /root/your-python-project
COPY . .

# Create a Python virtual environment
RUN python3 -m venv venv

# Activate the virtual environment and install required Python packages
RUN /bin/bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Command to run your Python script
CMD ["/bin/bash", "-c", "source venv/bin/activate && python3 batcher.py"]
