
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_cloudwatch_log_group" "packet_loggroup" {
  name              = "/aws/lambda/${lower(var.environmentName)}-packet"
  retention_in_days = "7"
}

data "archive_file" "packet_lambda_zip" {
  type        = "zip"
  source_dir = "${path.module}/functions"
  output_path = "${path.module}/packet.zip"
}

resource "aws_iam_role" "packet_lambda_role" {
  name = "${lower(var.environmentName)}-packet-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "processpipeline_lambda_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.packet_lambda_role.name
}

resource "aws_lambda_function" "packet_lambda" {
  filename         = data.archive_file.packet_lambda_zip.output_path
  function_name    = "${lower(var.environmentName)}-packet"
  role             = aws_iam_role.packet_lambda_role.arn
  handler          = "packet.lambda_handler"
  source_code_hash = data.archive_file.packet_lambda_zip.output_base64sha256
  runtime          = "python3.6"
  timeout          = 60

  environment {
    variables = {
      LOGLEVEL       = "INFO"
    }
  }

  tags = {
    Environment = var.environmentName
  }
}


