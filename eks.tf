###############################################################
# 1. SECURITY GROUP 
###############################################################
resource "aws_security_group" "eks_cluster" {
  name        = "eks-lab-cluster-sg"
  description = "EKS Cluster Security Group"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "eks-lab-cluster-sg" }
}

###############################################################
# 2. SECURITY GROUP
###############################################################
resource "aws_security_group" "eks_nodes" {
  name        = "eks-lab-nodes-sg"
  description = "EKS Nodes Security Group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "eks-lab-nodes-sg" }
}

###############################################################
# 3. EKS CLUSTER
###############################################################
resource "aws_eks_cluster" "main" {
  name     = "eks-lab"
  version  = "1.31"
  role_arn = aws_iam_role.cluster_role.arn

  vpc_config {
    subnet_ids = [
      aws_subnet.private_1.id,
      aws_subnet.private_2.id,
      aws_subnet.public_1.id,
      aws_subnet.public_2.id,
    ]
    security_group_ids      = [aws_security_group.eks_cluster.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
  ]

  tags = { Name = "eks-lab" }
}

###############################################################
# 4. NODE GROUP 
###############################################################
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "eks-lab-nodes"
  node_role_arn   = aws_iam_role.node_role.arn

  subnet_ids = [
    aws_subnet.private_1.id,
    aws_subnet.private_2.id,
  ]

  instance_types = ["t3.micro"]

  scaling_config {
    desired_size = 2
    min_size     = 1
    max_size     = 3
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [
    aws_eks_cluster.main,
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
  ]

  tags = { Name = "eks-lab-nodes" }
}

###############################################################
# 5. ACCESS ENTRY
###############################################################
resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.admin_role.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.admin_role.arn
  policy_arn    = "arn:aws:eks::aws:cluster-policy/AmazonEKSClusterAdminPolicy"

  access_scope { type = "cluster" }

  depends_on = [aws_eks_access_entry.admin]
}