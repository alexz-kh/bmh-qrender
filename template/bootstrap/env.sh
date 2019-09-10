#!/bin/bash

export BS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export DEBUG="true"
export KAAS_BM_ENABLED="true"
#
export KAAS_BM_AIO_VALUES="${BS_DIR}/values_ironic_aio.yaml"
export KAAS_BM_AIO_MGMT_VALUES="${BS_DIR}/mgmt_values_ironic_aio.yaml"
#
export KAAS_BM_METAL3_VALUES="${BS_DIR}/values_metal3.yaml"
export KAAS_BM_METAL3_MGMT_VALUES="${BS_DIR}/mgmt_values_metal3.yaml"
#
export KAAS_BM_PXE_IP="{{cookiecutter.pxe.provisioning_ip }}"
export KAAS_BM_PXE_BRIDGE="{{ cookiecutter.seed_host.bridge }}"
export KAAS_BM_PXE_MASK="{{ cookiecutter.pxe.provisioning_mask}}"
export KAAS_BM_LB_HOST="{{ cookiecutter.metallb.host }}"
#
export KAAS_BM_METALLB_MGMT_VALUES="${BS_DIR}/mgmt_values_metallb.yaml"
export KAAS_BM_MACHINES="${BS_DIR}/machine/all.yaml"
export KAAS_BM_HW="${BS_DIR}/hw/all.yaml"
#
export MASTER_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
export KEYCLOAK_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
export PROXY_FLOATING_IP="127.0.0.1"
export IAM_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
# IPs after pivoting
export KAAS_BM_MGMT_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"

function stubber(){

BSTGZ=https://artifactory.mcp.mirantis.net/binary-dev-local/kaas/bootstrap-linux-0.2.19-40-52bba0f.tar.gz
for n in 0 1 2 3; do
  sudo virsh destroy worker-${n} || true
done
qemu-imf create -f qcow2 /var/lib/libvirt/images/worker-0-0.qcow2 40G
set -x
mkdir -p $BS_DIR/dev
pushd $BS_DIR/dev/
if [[ ! -f bootstrap.tar.gz ]]; then
 wget ${BSTGZ} -O bootstrap.tar.gz
 tar -xzf bootstrap.tar.gz
fi
HOME=${BS_DIR}/dev/
export PATH=${PATH}:./bin/:./dev/
export KUBECTL_CMD="${BS_DIR}/dev/bin/kubectl"
./bin/kind delete cluster --name=clusterapi  || true
time ./bootstrap_new.sh all
popd
set +x
}
