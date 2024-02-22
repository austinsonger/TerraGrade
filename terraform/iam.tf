resource "aws_iam_role" "ec2_role" {
  name = "${local.resource_prefix}-ec2-role"
  assume_role_policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Action : "sts:AssumeRole",
        Principal : {
          Service : "ec2.amazonaws.com"
        },
        Effect : "Allow",
        Sid : ""
      }
    ]
  })

  tags = local.tags
}

resource "aws_iam_instance_profile" "bucket_instance_profile" {
  name = "${local.resource_prefix}-bucket-instance-profile"
  role = aws_iam_role.ec2_role.name

  tags = local.tags
}

resource "aws_iam_policy" "ec2_policy" {
  name        = "${local.resource_prefix}-ec2-policy"
  description = "Allows the EC2 instance to interact with various AWS services"
  policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect : "Allow",
        Action : [
          "s3:Put*",
          "s3:Get*",
          "s3:DeleteObject",
          "s3:List*"
        ],
        Resource : [
          "arn:aws:s3:::${var.s3_bucket_id}/${var.s3_folder_path}",
          "arn:aws:s3:::${var.s3_bucket_id}/${var.s3_folder_path}/*"
        ]
      },
      {
        Effect : "Allow",
        Action : ["ec2:DescribeInstances"],
        Resource : ["*"]
      }
    ]
  })

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "policy_attach" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_policy.arn
}