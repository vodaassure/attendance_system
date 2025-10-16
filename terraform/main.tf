terraform {
  required_providers {
    null = {
      source = "hashicorp/null"
    }
  }
}

resource "null_resource" "setup_playground" {
  connection {
    type        = "ssh"
    user        = var.ssh_user
    private_key = file(var.private_key_path)
    host        = var.server_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y git python3 python3-pip docker.io",
      "sudo systemctl enable docker",
      "sudo systemctl start docker",
      "sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose",
      "sudo chmod +x /usr/local/bin/docker-compose",
      "wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -",
      "sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'",
      "sudo apt-get update -y",
      "sudo apt-get install -y openjdk-11-jdk jenkins",
      "sudo systemctl enable jenkins",
      "sudo systemctl start jenkins",
      "echo Hello from Terraform"
    ]
  }
}


