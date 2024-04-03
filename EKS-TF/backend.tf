terraform {
  backend "s3" {
    bucket         = "chatbot-ui-v2"
    region         = "us-east-1"
    key            = "Chatbot-UIv2/EKS-TF/terraform.tfstate"
    dynamodb_table = "Lock-Files"
    encrypt        = true
  }
  required_version = ">=0.13.0"
}