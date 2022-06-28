resource "aws_ecs_cluster" "app" {
  name = "app"
}

resource "aws_ecs_service" "ebus_app" {
  name                   = "ebus_app"
  task_definition        = aws_ecs_task_definition.ebus_app.arn
  cluster                = aws_ecs_cluster.app.id
  launch_type            = "FARGATE"
  enable_execute_command = true
  desired_count          = 1

  network_configuration {
    assign_public_ip = false

    security_groups = [
      aws_security_group.egress_all.id,
      aws_security_group.ingress_api.id,
    ]

    subnets = [
      aws_subnet.private_d.id,
      aws_subnet.private_e.id,
    ]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ebus_app.arn
    container_name   = "ebus-app"
    container_port   = "9202"
  }
}

resource "aws_cloudwatch_log_group" "ebus_app" {
  name = "/ecs/ebus-app"
}

resource "aws_ecs_task_definition" "ebus_app" {
  family     = "ebus-app"
  depends_on = [aws_db_instance.ebus-app]

  container_definitions = <<EOF
  [
    {
      "name": "ebus-app",
      "image": "617542518433.dkr.ecr.us-east-1.amazonaws.com/breakable-toy-luke:latest",
      "portMappings": [
        {
          "containerPort": 9202
        }
      ],
      "environment": [
        {
            "name": "RDS_DB_NAME",
            "value": "${var.rds_db_name}"
        },
        {
            "name": "RDS_USERNAME",
            "value": "${var.rds_username}"
        },
        {
            "name": "RDS_PASSWORD",
            "value": "${var.rds_password}"
        },
        {
            "name": "RDS_HOSTNAME",
            "value": "${aws_db_instance.ebus-app.address}"
        },
        {
            "name": "RDS_PORT",
            "value": "5432"
        }
        ],

      "command": ["-w", "1", "-b", "0.0.0.0:9202", "--reload", "--log-level", "info", "--error-logfile", "-", "--forwarded-allow-ips", "*", "-k", "gevent", "ebusserver.wsgi"],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "us-east-1",
          "awslogs-group": "/ecs/ebus-app",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
  EOF

  task_role_arn      = aws_iam_role.ebus_app_task_role.arn
  execution_role_arn = aws_iam_role.ebus_app_task_execution_role.arn

  # Minimum values for Fargate containers.
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  requires_compatibilities = ["FARGATE"]

  # Required for Fargate containers 
  network_mode = "awsvpc"
}

resource "aws_lb_target_group" "ebus_app" {
  name        = "ebus-app"
  port        = 9202
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.app_vpc.id

  health_check {
    enabled = true
    path    = "/ping/"
  }

  depends_on = [aws_alb.ebus_app]
}

resource "aws_alb" "ebus_app" {
  name               = "ebus-app-lb"
  internal           = false
  load_balancer_type = "application"

  subnets = [
    aws_subnet.public_d.id,
    aws_subnet.public_e.id,
  ]

  security_groups = [
    aws_security_group.http.id,
    aws_security_group.https.id,
    aws_security_group.egress_all.id,
  ]

  depends_on = [aws_internet_gateway.igw]
}

resource "aws_alb_listener" "ebus_app_http" {
  load_balancer_arn = aws_alb.ebus_app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ebus_app.arn
  }
}

output "alb_url" {
  value = "http://${aws_alb.ebus_app.dns_name}"
}
