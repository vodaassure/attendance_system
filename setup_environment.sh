#!/bin/bash

set -e

echo "🔄 Updating package index..."
sudo apt-get update

echo "📦 Installing required packages..."
sudo apt-get install -y ca-certificates curl apt-transport-https software-properties-common wget fontconfig openjdk-21-jre gnupg

echo "📁 Creating keyring directory..."
sudo install -m 0755 -d /etc/apt/keyrings

echo "🔑 Adding Docker's official GPG key..."
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "📝 Adding Docker repository to Apt sources..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"${UBUNTU_CODENAME:-$VERSION_CODENAME}\") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "🔄 Updating package index again..."
sudo apt-get update

echo "📦 Installing Docker packages..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "🚀 Starting Docker service..."
sudo systemctl start docker

echo "🔍 Checking Docker service status..."
sudo systemctl status docker

echo "👤 Adding current user '$USER' to the 'docker' group..."
sudo usermod -aG docker $USER

echo "✅ Docker installation complete!"
echo "🔄 Please log out and log back in (or restart your session) for group changes to take effect."
echo "🧪 After re-login, verify Docker access with: docker run hello-world"

echo "📦 Installing Docker Compose plugin..."
sudo apt install -y docker-compose-plugin
docker compose version

echo "📦 Installing Jenkins..."
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install -y jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins

echo "📦 Installing Git..."
sudo apt install -y git
git --version

echo "📦 Installing kubectl (optional)..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
sudo apt-get install -y kubectl

echo "📦 Installing Minikube (optional)..."
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
minikube start

echo "📦 Installing Grafana (optional)..."
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana

echo "✅ All installations completed!"
