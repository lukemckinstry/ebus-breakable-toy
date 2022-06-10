# Deployment


## AWS Credentials

Provide your AWS credentials in order to authenticate. Define them as environment variables:

```bash
$ export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
$ export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
```

You will be prompted to enter your AWS credentials, along with a default region. These credentials will be used to authenticate calls to the AWS API when using Terraform and the AWS CLI.

## Terraform

To deploy this project's core infrastructure, use the following script to lookup the remote state of the infrastructure and assemble a plan for work to be done:

```bash
$ ./scipts/infra plan
```

Once the plan has been assembled, and you agree with the changes, apply it:

```bash
$ terraform apply
```

## AWS Exec

Exec into the running app container

```bash
$ aws ecs execute-command --region us-east-1 --cluster app --task <ENTER-TASK-ID-HERE> --container sun-api --command "/bin/bash" --interactive
```