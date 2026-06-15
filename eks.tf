###############################################################
# eks.tf
# Creates:
#   1. Security Groups (firewall rules for cluster and nodes)
#   2. EKS Control Plane (the managed Kubernetes master)
#   3. EKS Managed Node Group (the EC2 worker nodes)
#   4. EKS Access Entry (RBAC link for the admin role)
###############################################################

###############################################################
# SECURITY GROUPS
# Think of these as firewall rules for the cluster components.
###############################################################



# ── Security Group: EKS Control Plane ─────────────────────────
# The API server (control plane) needs to talk to worker nodes
resource "aws_security_group" "cluster_sg" {
  name        = "${var.project}-cluster-sg"
  description = "Security group for EKS control plane"
  vpc_id      = aws_vpc.main.id

  # Allow all outbound traffic from the control plane
  egress 
 {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"   
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project}-cluster-sg" }
}





# ── Security Group: Worker Nodes ───────────────────────────────
# Nodes need to talk to each other and to the control plane
resource "aws_security_group" "node_sg" {
  name        = "${var.project}-node-sg"
  description = "Security group for EKS worker nodes"
  vpc_id      = aws_vpc.main.id

  # Nodes talk to each other freely (pod-to-pod traffic)
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true   # Allow traffic from other nodes in same SG
  }

  # Control plane talks to nodes (kubelet port 10250 + NodePort range)
  ingress {
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.cluster_sg.id]
  }

  # Nodes can reach the internet (for pulling images via NAT)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project}-node-sg" }
}





###############################################################
# EKS CONTROL PLANE
# This is the "brain" of Kubernetes — managed by AWS.
# You don't see these servers; AWS handles them for you.
# Includes: API server, etcd, scheduler, controller manager.
###############################################################

resource "aws_eks_cluster" "main" {
  name     = "${var.project}-eks"
  version  = "1.31"                       # Latest stable as of 2025
  role_arn = aws_iam_role.node_role.arn   # Control plane uses node role for AWS API calls

  vpc_config {
    # Which subnets the control plane can place ENIs into
    subnet_ids = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id,
      aws_subnet.public_a.id,
      aws_subnet.public_b.id,
    ]

    security_group_ids      = [aws_security_group.cluster_sg.id]
    endpoint_private_access = true    # Nodes talk to API server privately
    endpoint_public_access  = true    # You can run kubectl from your laptop
  }

  # Enable control plane logging (free — stored in CloudWatch)
  enabled_cluster_log_types = ["api", "audit"]

  # EKS must wait until node role policies are attached
  depends_on = [
    aws_iam_role_policy_attachment.node_eks,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
  ]

  tags = { Name = "${var.project}-eks" }
}







###############################################################
# EKS MANAGED NODE GROUP
# These are the actual EC2 instances that run your pods.
# "Managed" means AWS handles OS patching and node replacement.
# We use 2 nodes (one per AZ for the diagram) — still cheap.
###############################################################

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project}-nodes"
  node_role_arn   = aws_iam_role.node_role.arn

  # Place nodes in PRIVATE subnets (more secure — no public IPs)
  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
  ]

  # ── Instance settings ────────────────────────────────────────
  instance_types = ["t3.micro"]   # Free tier eligible!
  disk_size      = 5             # GB — minimum for EKS (default is 20)

  scaling_config {
    desired_size = 2
    min_size     = 1
    max_size     = 3
  }

  update_config {
    max_unavailable = 1
  }

  # Nodes must wait for the cluster to be ready
  depends_on = [aws_eks_cluster.main]

  tags = { Name = "${var.project}-node-group" }
}





###############################################################
# EKS ACCESS ENTRY
# This is the "RBAC Link" shown in the diagram.
# It connects the admin IAM role to Kubernetes RBAC.
# Without this: even if you have the IAM role, kubectl is denied.
# With this: the IAM role maps to cluster-admin in Kubernetes.
# This replaced the old aws-auth ConfigMap approach in EKS 1.21+.
###############################################################

# Create the access entry — "this IAM role can access this cluster"
resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.admin_role.arn
  type          = "STANDARD"   # Regular IAM user/role (not node or Fargate)

  tags = { Name = "${var.project}-admin-access-entry" }
}

# Associate the access entry with a policy — "give it cluster-admin"
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.admin_role.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"   # Full cluster access (not limited to a namespace)
  }

  depends_on = [aws_eks_access_entry.admin]
}
