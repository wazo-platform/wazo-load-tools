terraform {
  required_version = ">= 1.11.0"
  required_providers {
    template = {
      source  = "hashicorp/template"
      version = "~> 2.2.0"
    }
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 3.0.0"
    }
  }
}

provider "openstack" {
  user_name     = var.user_name
  password      = var.password
  tenant_name   = var.tenant_name
  domain_name   = var.domain_name
  auth_url      = var.auth_url
  endpoint_type = var.endpoint_type
}

data "template_cloudinit_config" "monitor" {
  dynamic "part" {
    for_each = var.cloud_config_files
    iterator = filename
    content {
      content_type = "text/cloud-config"
      content      = file(filename.value)
      merge_type   = "list(append)+dict(recurse_list)+str()"
    }
  }
}

resource "openstack_compute_instance_v2" "monitor" {
  name              = var.instance_name
  region            = var.region
  image_name        = var.image_name
  flavor_name       = var.flavor_name
  key_pair          = var.key_pair
  availability_zone = var.availability_zone

  user_data = data.template_cloudinit_config.monitor.rendered

  security_groups = ["default"]

  network {
    name = var.network
  }
}

data "openstack_networking_port_v2" "vm-port" {
  device_id  = openstack_compute_instance_v2.monitor.id
  network_id = openstack_compute_instance_v2.monitor.network.0.uuid
}

resource "openstack_networking_floatingip_associate_v2" "floatingip" {
  floating_ip = var.floating_ip
  port_id     = data.openstack_networking_port_v2.vm-port.id
}

// Volume is not created by terraform to avoid to split data between volumes in
// case we lose terraform state
resource "openstack_compute_volume_attach_v2" "prometheus" {
  instance_id = openstack_compute_instance_v2.monitor.id
  volume_id   = var.volume_id
}
