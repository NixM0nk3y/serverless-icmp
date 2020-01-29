module "invokeuser" {
  source    = "git::https://github.com/cloudposse/terraform-aws-iam-system-user.git?ref=master"
  namespace = "openenterprise"
  stage     = "develop"
  name      = "packetinvoke"
}


data "aws_iam_policy_document" "invoke_policy" {
  statement {
    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      aws_lambda_function.packet_lambda.arn
    ]
  }
}

resource "aws_iam_user_policy" "invoke_policy" {
  name   = module.invokeuser.user_name
  user   = module.invokeuser.user_name
  policy = data.aws_iam_policy_document.invoke_policy.json
}
