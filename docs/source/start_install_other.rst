

# Installation in virtual machine

You can install mCloud on any virtual machine of latest Ubuntu build. So if you already have the virtual machine up and running please follow [Linux installation](start_install_linux.html) guide. 

## 1. Install Vagrant

Follow guide at [Vagrant website](https://www.vagrantup.com) to get it installed.

## 2. Prepare project directory

Create empty directory for your new deployment and download Vagrantfile into it:

    curl https://raw.githubusercontent.com/modera/mcloud-samples/master/Vagrantfile -O

## 3. Provision and start new machine

Run vagrant command from the project directory where Vagrantfile is located.,

    vagrant up

Wait until vagrant is downloading images and preparing the machine. Provision script tells vagrant to do following:

* start up empty Ubuntu machine
* install Docker
* install mCloud and dependencies
* start everything

## 4. Log into mCloud terminal

To use mCloud command-line type:

    $ vagrant ssh

Now you're in Ubuntu command line. 

    $ mcloud

This starts up mCloud terminal, so you can type commands to manage your deployments:

    mcloud: ~@me>

## Next steps

Proceed to [Hello World guide](start_hello.html) that describes how to set up a simplest deployment with a webserver and static page.

Or in case you feel confident enough you can jump to [Multi-service deployment guide](start_multiserver.html) to see how to set up bit more complex deployment with multiple tiers.


