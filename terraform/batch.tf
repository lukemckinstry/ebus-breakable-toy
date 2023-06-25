resource "aws_batch_compute_environment" "batch" {
  compute_environment_name = "my-project-compute-env"

  compute_resources {

    max_vcpus = 256

    security_group_ids = [
      aws_security_group.egress_all.id
    ]

    subnets = [aws_subnet.private_d.id, aws_subnet.private_e.id]

    type = "FARGATE"
  }

  service_role = aws_iam_role.aws_batch_service_role.arn
  type         = "MANAGED"
  depends_on = [
    aws_iam_role_policy_attachment.aws_batch_service_role
  ]
}

resource "aws_batch_job_queue" "batch" {
  name     = "my-project-job-queue"
  state    = "ENABLED"
  priority = "0"
  compute_environments = [
    aws_batch_compute_environment.batch.arn,
  ]
}

resource "aws_batch_job_definition" "batch" {
  name = "my-project-job-definition"
  type = "container"
  platform_capabilities = [
    "FARGATE",
  ]
  container_properties = jsonencode({
    command    = ["/usr/local/src/process_upload.py"]
    image      = "617542518433.dkr.ecr.us-east-1.amazonaws.com/breakable-toy-batch-upload:latest"

    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }

    networkConfiguration = {
      assignPublicIp = "ENABLED"
    }

    resourceRequirements = [
      {
        type  = "VCPU"
        value = "0.25"
      },
      {
        type  = "MEMORY"
        value = "512"
      }
    ]

    executionRoleArn = aws_iam_role.ebus_app_task_execution_role.arn
  })
}
