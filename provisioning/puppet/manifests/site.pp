# -*- mode: ruby -*-
# vi: set ft=node default {

node default {
  $project_root = '/vagrant'

  yumrepo { "epel":
    descr      => 'epel',
    mirrorlist => 'http://mirrors.fedoraproject.org/mirrorlist?repo=epel-6&arch=$basearch',
    enabled    => 1,
    gpgcheck   => 0
  }
  Yumrepo <| |> -> Package <| |>

  # Firewall
  service { 'iptables':
    enable => true,
    ensure => running
  }
  file { '/etc/sysconfig/iptables':
    ensure => present,
    source => '/vagrant/provisioning/puppet/manifests/files/iptables',
    owner  => 'root',
    group  => 'root',
    mode   => '0600'
  }
  File['/etc/sysconfig/iptables'] ~> Service['iptables']

  package { 'git':
    ensure => latest
  }

  # python
  package { 'centos-release-SCL':
    ensure => installed
  }
  package {'python27':
    ensure => installed
  }
  file { '/home/vagrant/.bashrc':
    source => '/vagrant/provisioning/puppet/manifests/files/bashrc',
    owner  => 'vagrant',
    group  => 'vagrant',
    mode   => '0644'
  }
  Package['centos-release-SCL'] -> Package['python27'] -> File['/home/vagrant/.bashrc']
}
