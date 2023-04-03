#!/bin/bash
set -xe
src_dir=$(cd $(dirname "$0")/../.. && pwd -P)

podman run --rm -d --network uyuni-network-1 -v /tmp/test-all-in-one:/tmp -v ${src_dir}/testsuite/podman_runner/salt-minion-entry-point.sh:/salt-minion-entry-point.sh --name deblike_minion -h deblike_minion ghcr.io/$UYUNI_PROJECT/uyuni/ci-test-ubuntu-minion:$UYUNI_VERSION bash -c "/salt-minion-entry-point.sh uyuni-server-all-in-one-test 1-DEBLIKE-KEY"
podman exec deblike_minion bash -c "ssh-keygen -A && /usr/sbin/sshd -e"
podman exec deblike_minion bash -c "if [ ! -d /root/.ssh ];then mkdir /root/.ssh/;chmod 700 /root/.ssh;fi;cp /tmp/authorized_keys /root/.ssh/"