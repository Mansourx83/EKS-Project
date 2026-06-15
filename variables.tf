###############################################################
# variables.tf
# All inputs in one place — change aws_region if needed.
###############################################################

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"   # Change to your nearest region
}

variable "project" {
  description = "Prefix for every resource name — keeps things tidy"
  type        = string
  default     = "eks-lab"
}
