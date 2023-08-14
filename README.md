# Network Topology and Routing Configuration

This repository contains scripts to set up a network topology using Mininet and configure routing rules using the POX controller.

## Table of Contents

- [Overview](#overview)
- [Network Topology](#network-topology)
- [Routing Configuration](#routing-configuration)
- [Usage](#usage)

## Overview

The codebase is divided into two main parts:

1. A Mininet script that defines a custom network topology.
2. A POX controller script that handles packet routing based on specific rules.

## Network Topology

The Mininet script sets up the following network topology:

- Hosts:
  - Sales Department: Laptop1, Laptop2, Printer
  - IT Department: ws3, ws4
  - OT Department: ws1, ws2
  - Datacenter: DNSserver, Webserver, Server2
- Switches: s1, s2, s3, s4, coreswitch

Each host is connected to a specific switch, and the switches are interconnected through the coreswitch.

## Routing Configuration

The POX controller script defines routing rules based on packet types:

1. ICMP traffic is forwarded only between the Sales Department, IT Department, and OT Department subnets or between devices on the same subnet.
2. TCP traffic is forwarded only between the Datacenter, IT Department, and OT Department subnets or between devices on the same subnet.
3. UDP traffic is forwarded only between the Sales Department and Datacenter subnets or between devices on the same subnet.

## Usage

To use the scripts:

1. Run the Mininet script to set up the network topology.
2. Launch the POX controller with the provided script to handle packet routing.

Ensure you have both Mininet and POX installed and configured on your system.

---

**Note**: Always review and test the scripts in a controlled environment before deploying in a production network.
