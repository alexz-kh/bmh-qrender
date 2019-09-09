BS_DIR="${HOME}/bootstrap"
export DEBUG="true"
export KAAS_BM_AIO_VALUES="${BS_DIR}values_ironic_aio.yaml"
export KAAS_BM_METAL3_VALUES="${BS_DIR}/values_metal3.yaml"
export KAAS_BM_ENABLED="true"

export KAAS_BM_PXE_BRIDGE="{{ cookiecutter.seed_host.bridge }}"
export KAAS_BM_PXE_IP="{{cookiecutter.pxe.provisioning_ip }}"
export KAAS_BM_PXE_MASK="{{ cookiecutter.pxe.provisioning_mask}}"
export MASTER_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
export KEYCLOAK_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
export PROXY_FLOATING_IP="127.0.0.1"
export IAM_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
# IPs after pivoting
export KAAS_BM_MGMT_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"


PATH=${PATH}:./bin/:./1/
export KUBECTL_CMD="${HOME}/cluster-api-provider-openstack/bootstrap/bin/kubectl"

function stubber{

time ./1/clusterctl bootstrap create \
  --metallb-chart-version 0.9.7 \
  --metallb-values ${HOME}/bootstrap/values_metallb.yaml \
  --metallb-mgmt-values ${HOME}/bootstrap/values_metallb.yaml \
  --ironic-values ${HOME}/bootstrap/values_ironic_aio.yaml \
  --ironic-mgmt-values ${HOME}/bootstrap/mgmt_values_ironic_aio.yaml \
  --ironic-chart-version 0.2.0 \
  --metal3-chart-version 0.2.0 \
  --metal3-mgmt-values ${HOME}/bootstrap/mgmt_values_metal3.yaml \
  --metal3-values ${HOME}/bootstrap/values_metal3.yaml \
  --baremetalhosts ${HOME}/bootstrap/hw/all.yaml \
  --provider baremetal \
  --bootstrap-cluster-name clusterapi \
  --os-cloud openstack \
  --keyname '' \
  --external-network-id '' \
  --cluster-name test1 \
  --artifactory-repo dev \
  --chart-repo https://artifactory.mcp.mirantis.net/helm-dev-virtual \
  --version $(cat .version | awk '{print $1}') \
  --iam-registration-url 10.0.0.23:8082 \
  --cluster ${HOME}/bootstrap/cluster.yaml \
  --machines ${HOME}/bootstrap/machine/all.yaml \
  --release-path $CAPO_DIR/bootstrap/1/releases/ \
  --chart-dir $CAPO_DIR/charts/ \
  --v 4


}
