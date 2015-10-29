# -*- mode: ruby -*-
# vi: set ft=ruby :

require "yaml"

params = YAML::load_file("./Vagrantparams.yml")

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = params['box']
  config.vm.box_url = params['box_url']
  config.vm.hostname = 'pyzlog.local'

  config.vm.network :forwarded_port, guest: params['guest_port'], host: params['host_port'], auto_correct: true
  config.vm.network :private_network, :ip => params['ip']
  config.vm.synced_folder ".", "/vagrant", :nfs => params['nfs']

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", params['memory']]
    vb.customize ["modifyvm", :id, "--cpus", params['cpus']]
  end

  # Install puppet module dependencies
  config.vm.provision "shell", inline: "yum install -y -q ruby-devel git"
  config.vm.provision "shell", inline: "gem list|grep librarian-puppet || gem install librarian-puppet -v 1.4.0"
  config.vm.provision "shell", inline: "cd /vagrant/provisioning/puppet && librarian-puppet install"

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "provisioning/puppet/manifests"
    puppet.manifest_file  = "site.pp"
    puppet.options        = ['--modulepath=/vagrant/provisioning/puppet/modules']
  end

  scriptPath = "./provisioning/puppet/manifests/scripts/startup.sh"
  config.vm.provision "shell", privileged: false, path: scriptPath
end
