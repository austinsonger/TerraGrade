resource "aws_eip" "eip" {
  instance = aws_instance.app_server.id
  domain   = "vpc"

  tags = local.tags
}

resource "aws_eip_association" "eip_association" {
  instance_id   = aws_instance.app_server.id
  allocation_id = aws_eip.eip.id
}
