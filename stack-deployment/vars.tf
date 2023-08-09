variable "instance_nb" {
  default = 1
}

variable "user_name" {
  description = "Openstack username."
  default = "jenkins-community"
}

variable "password" {
  description = "Openstack password."
  default = "< OPENSTACK PASSWORD >"
}

variable "tenant_name" {
  description = "Openstack Tenant name."
  default = "< ACCOUNT NAME >"
}

variable "domain_name" {
  description = "Openstack Tenant name."
  default     = "default"
}

variable "auth_url" {
  description = "Openstack keystone URL."
  default = "http://openstack-controller-1.lan.wazo.io:5000/v3"
}

variable "endpoint_type" {
  description = "Openstack endpoint type use from service catalog."
  default     = "internal"
}

variable "region" {
  description = "Openstack region name."
  default     = "RegionOne"
}

variable "image_id" {
  description = "Openstack image id."
  default = "< OPENSTACK IMAGE ID >"
}

variable "flavor_id" {
  description = "OPENSTACK FLAVOR DESCRIPTION >"
  default     = "< OPENSTACK FLAVIOR ID >"
}

variable "key_pair" {
  description = "Openstack key pair name."
  default = "< KEY PAIR NAME >"
}

variable "network" {
  description = "Openstack network."
  default = "< NETWORK NAME >"
}

variable "key_file" {
  description = "SSH private key file path"
  default = "< PRIVATE KEY PATH >"
}

variable "availability_zone" {
  description = "Openstack availability zone."
  default = "nova"
}
