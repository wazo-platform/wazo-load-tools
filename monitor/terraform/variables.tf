
variable "region" {
  description = "AWS region."
}

variable "default_tags" {
  description = "AWS default tags"
  default     = {}
}

variable "ami_name_filter" {
  description = "Filter to apply on names to retrieve AMI"
  type        = string
  default     = "debian-12*"
}

variable "instance_type" {
  description = "AWS instance type."
}

variable "instance_user" {
  description = "Default instance user"
}

variable "subnet_id" {
  description = "AWS subnet ID."
}

variable "keypair_name" {
  description = "Key Pair name"
  type        = string
  default     = "monitor"
}

variable "public_key_path" {
  description = "Path to ssh public key file to use to deploy instances."
  type        = string
}

variable "security_group_ids" {
  type        = list(string)
  description = "List of VPC security group IDs."
  default     = []
}

variable "volume_size" {
  description = "EBS volume size to use for prometheus data"
  type        = number
  default     = 20
}

variable "cloud_config_files" {
  type        = list(string)
  description = "cloud-config files to append to monitor instance cloud-config."
  default     = []
}
