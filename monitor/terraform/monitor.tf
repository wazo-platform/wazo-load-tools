provider "aws" {
  region = var.region
  default_tags {
    tags = var.default_tags
  }
}

resource "aws_key_pair" "monitor" {
  key_name   = var.keypair_name
  public_key = file(var.public_key_path)
}

data "cloudinit_config" "monitor" {
  dynamic "part" {
    for_each = concat(
      ["${path.module}/files/cloud-init.yml"],
      var.cloud_config_files,
    )
    iterator = filename
    content {
      content_type = "text/cloud-config"
      content      = templatefile(filename.value, {
        user       = var.instance_user,
      })
      merge_type   = "list(append)+dict(recurse_list)+str()"
    }
  }
}

data "aws_ami" "monitor" {
  most_recent = true
  owners      = ["self", "amazon"]

  filter {
    name   = "name"
    values = [var.ami_name_filter]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

data "aws_subnet" "monitor" {
  id = var.subnet_id
}

resource "aws_instance" "monitor" {
  ami           = data.aws_ami.monitor.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.monitor.key_name
  subnet_id     = var.subnet_id

  user_data_base64 = data.cloudinit_config.monitor.rendered

  vpc_security_group_ids = var.security_group_ids
}

resource "aws_volume_attachment" "prometheus" {
  device_name = "/dev/sdb"
  instance_id = aws_instance.monitor.id
  volume_id   = aws_ebs_volume.prometheus.id
}

resource "aws_ebs_volume" "prometheus" {
  availability_zone = data.aws_subnet.monitor.availability_zone
  size              = var.volume_size
}
