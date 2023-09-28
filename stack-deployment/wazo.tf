terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.48.0"
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

resource "openstack_compute_instance_v2" "wazo-stack-test" {
  name              = "wazo-stack-test${count.index}"
  region            = var.region
  image_id          = var.image_id
  flavor_id         = var.flavor_id
  key_pair          = var.key_pair
  availability_zone = var.availability_zone

  count = var.instance_nb
  user_data = file("cloud-init.yml")

  security_groups = [
    "default"
  ]
  network {
    name = var.network
  }

  connection {
    host        = "openstack.lan.wazo.io"
    user        = "jenkins"
    private_key = file(var.key_file)
    agent       = false
  }

}

resource "openstack_networking_floatingip_v2" "fip_1" {
  count = var.instance_nb
  pool  = "provider"
}

resource "openstack_compute_floatingip_associate_v2" "fip_1" {
  count       = var.instance_nb
  floating_ip = openstack_networking_floatingip_v2.fip_1[count.index].address
  instance_id = openstack_compute_instance_v2.wazo-stack-test[count.index].id
}


output "ips" {
  value = join(" ", openstack_compute_instance_v2.wazo-stack-test.*.access_ip_v4)
}
