from azureml.core import Workspace
from azureml.core.compute import AksCompute, ComputeTarget

# Set the resource group that contains the AKS cluster and the cluster name
resource_group = 'rappi_rg'
cluster_name = 'rappi-cp-cluster'
aks_name = 'titanicaks'

ws = Workspace.from_config()

# Attach the cluster to your workgroup. If the cluster has less than 12 virtual CPUs, use the following instead:
# attach_config = AksCompute.attach_configuration(resource_group = resource_group,
#                                         cluster_name = cluster_name,
#                                         cluster_purpose = AksCompute.ClusterPurpose.DEV_TEST)
attach_config = AksCompute.attach_configuration(resource_group=resource_group,
                                                cluster_name=cluster_name)
aks_target = ComputeTarget.attach(ws, aks_name, attach_config)

# Wait for the attach process to complete
aks_target.wait_for_completion(show_output=True)
