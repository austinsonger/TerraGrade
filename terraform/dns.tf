provider "acme" {
  server_url = var.enable_ssl_staging ? "https://acme-staging-v02.api.letsencrypt.org/directory" : "https://acme-v02.api.letsencrypt.org/directory"
}

resource "aws_route53_record" "subdomain_record" {
  zone_id = var.hosted_zone_id
  name    = "${var.subdomain_name}.${var.hosted_zone_name}"
  type    = "A"
  records = [aws_eip.eip.public_ip]
  ttl     = "180"
}

resource "tls_private_key" "private_key" {
  algorithm = "RSA"
}

resource "acme_registration" "registration" {
  account_key_pem = tls_private_key.private_key.private_key_pem
  email_address   = var.dns_email_address
}

resource "acme_certificate" "certificate" {
  account_key_pem           = acme_registration.registration.account_key_pem
  common_name               = var.hosted_zone_name
  subject_alternative_names = ["${var.subdomain_name}.${var.hosted_zone_name}"]

  dns_challenge {
    provider = "route53"

    config = {
      AWS_HOSTED_ZONE_ID = var.hosted_zone_id
    }
  }

  depends_on = [acme_registration.registration]
}

resource "aws_acm_certificate" "certificate" {
  certificate_body  = acme_certificate.certificate.certificate_pem
  private_key       = acme_certificate.certificate.private_key_pem
  certificate_chain = acme_certificate.certificate.issuer_pem
}