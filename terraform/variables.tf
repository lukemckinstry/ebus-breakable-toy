
variable "rds_db_name" {
  description = "RDS database name"
  default     = "mydb"
}
variable "rds_username" {
  description = "RDS database username"
  default     = "foo"
}
variable "rds_password" {
  description = "RDS database password"
  default     = "foofoofoo"
}
variable "rds_instance_class" {
  description = "RDS instance type"
  default     = "db.t3.micro"
}
variable "rds_port" {
  description = "RDS port"
  default     = "5432"
}
variable "rds_engine" {
  description = "RDS engine"
  default     = "postgres"
}
variable "rds_enigne_version" {
  description = "RDS engine version"
  default     = "14.7"
}
variable "ecs_cpu" {
  description = "ECS cpu parameter"
  default     = 512
  type        = number
}
variable "ecs_memory" {
  description = "ECS memory parameter"
  default     = 1024
  type        = number
}


