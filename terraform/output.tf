output "jenkins_url" {
  description = "URL to access Jenkins on the playground server"
  value       = "http://${var.server_ip}:8080"
}

output "docker_status" {
  description = "Docker service status after provisioning"
  value       = "Use 'systemctl status docker' on the server to verify Docker is running."
}

output "flask_app_url" {
  description = "URL to access the Flask Attendance App"
  value       = "http://${var.server_ip}:5000"
}
