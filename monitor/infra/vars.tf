
variable "user_name" {
  description = "Openstack username."
}

variable "password" {
  description = "Openstack password."
}

variable "tenant_name" {
  description = "Openstack Tenant name."
}

variable "domain_name" {
  description = "Openstack Domain name."
  default     = "default"
}

variable "auth_url" {
  description = "Openstack keystone URL."
}

variable "endpoint_type" {
  description = "Openstack endpoint type use from service catalog."
  default     = "internal"
}

variable "region" {
  description = "Openstack region name."
  default     = "RegionOne"
}

variable "availability_zone" {
  description = "Openstack availability zone."
}

variable "instance_name" {
  description = "Instance name"
  default     = "monitor"
}

variable "key_pair" {
  description = "Openstack key pair name."
}

variable "image_name" {
  description = "Openstack image name."
}

variable "flavor_name" {
  description = "Openstack flavor name."
}

variable "network" {
  description = "Openstack network."
}

variable "key_file" {
  description = "SSH private key file path"
}

variable "floating_ip" {
  description = "Floating IP (must be created manually)"
}

variable "volume_id" {
  description = "Volume ID to use for prometheus data (must be created and formatted to ext4 manually)"
}

variable "cloud_config_files" {
  type = list
  description = "cloud config files to use. Useful to extend default commands by providing custom files"
  default = ["cloud-init.yml"]
}
