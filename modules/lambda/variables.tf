variable "function_name" {
  type = string
}

variable "environment" {
  type    = map(string)
  default = {}
}

variable "memory_size" {
  type    = number
  default = 256
}

variable "timeout" {
  type    = number
  default = 60
}
