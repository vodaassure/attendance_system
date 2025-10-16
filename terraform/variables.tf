variable "ssh_user" {
  description = "SSH username for the playground server"
  type        = string
  default     = "cloud_user"
}

variable "private_key_path" {
  description = "Path to the SSH private key file"
  type        = string
  default     = "~/.ssh/id_rsa"
}

variable "server_ip" {
  description = "IP address of the Pluralsight playground server"
  type        = string
}

