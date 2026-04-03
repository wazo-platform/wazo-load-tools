output "instance_id" {
  value = aws_instance.monitor.id
}

output "instance_private_ip" {
  value = aws_instance.monitor.private_ip
}
