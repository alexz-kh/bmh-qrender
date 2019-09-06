BS_DIR="${HOME}/bootstrap"
export DEBUG="true"
export KAAS_BM_AIO_VALUES="${BS_DIR}values_ironic_aio.yaml"
export KAAS_BM_METAL3_VALUES="${BS_DIR}/values_metal3.yaml"
export KAAS_BM_ENABLED="true"

export KAAS_BM_PXE_BRIDGE={{cookiecutter.seed_host.bridge}}
export KAAS_BM_PXE_IP="{{cookiecutter.pxe.provisioning_ip + '/' +  cookiecutter.pxe.provisioning_mask}}"
export MASTER_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
export KEYCLOAK_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
export PROXY_FLOATING_IP="127.0.0.1"
export IAM_FLOATING_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
# IPs after piviting
export KAAS_BM_MGMT_IP="{{ cookiecutter.nodes.master.n0.dhcp_ip }}"
