
resource "aws_s3_bucket" "joshfarwell-hashhouse" {
  bucket = "joshfarwell-hashhouse"
  acl    = "private"

  tags = {
    Name        = "Hash House"
    foo         = "bar"
  }
}


resource "aws_iam_user" "hashhouse" {
  name = "hashhouse"

  tags = {
    foo = "bar"
  }
}


resource "aws_iam_access_key" "hashhouse" {
  user = aws_iam_user.hashhouse.name
}


resource "aws_iam_user_policy" "hashhouse-s3" {
  name = "hashhouse-s3"
  user = aws_iam_user.hashhouse.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::joshfarwell-hashhouse"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": ["arn:aws:s3:::joshfarwell-hashhouse/*"]
    }
  ]
}
EOF
}
