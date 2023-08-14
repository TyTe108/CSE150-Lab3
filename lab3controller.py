#
# Hints/Reminders from Lab 3:
#
# To check the source and destination of an IP packet, you can use
# the header information... For example:

# To send an OpenFlow Message telling a switch to send packets out a
# port, do the following, replacing <PORT> with the port number the 
# switch should send the packets out:
#
#    msg = of.ofp_flow_mod()
#    msg.match = of.ofp_match.from_packet(packet)

#    msg.actions.append(of.ofp_action_output(port = <PORT>))
#    msg.data = packet_in
#    self.connection.send(msg)
#
# To drop packets, simply omit the action.
#

from pox.core import core

import pox.openflow.libopenflow_01 as of

log = core.getLogger()

def ip_to_binary_array(ip_str):
  ip_parts = ip_str.split(".")
  binary_array = []
  for part in ip_parts:
    binary_part = format(int(part), "08b")
    for char in binary_part:
      binary_array.append(int(char))
  return binary_array

def compare_first_n_elements(arr1, arr2, n):
  if len(arr1) < n or len(arr2) < n:
    return False
  for i in range(n):
    if arr1[i] != arr2[i]:
      return False
  return True

def check_valid_ip(ip, subnet, mask):
  ip_array = ip_to_binary_array(ip)
  subnet_array = ip_to_binary_array(subnet)
  return compare_first_n_elements(ip_array, subnet_array, mask)

class Routing (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)
  


  def do_routing (self, packet, packet_in, port_on_switch, switch_id):
    # port_on_swtich - the port on which this packet was received
    # switch_id - the switch which received this packet

    def accept(port_num):
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.idle_timeout = 30
      msg.actions.append(of.ofp_action_output(port=port_num))
      msg.buffer_id = packet_in.buffer_id
      self.connection.send(msg)

    

    #print ("Dest Port: " + str(port_on_switch))

    arp_packet = packet.find('arp')
    tcp_packet = packet.find('tcp')
    ipv4_packet = packet.find('ipv4')
    icmp_packet = packet.find('icmp')
    udp_packet = packet.find('udp')

    sales_subnet = "10.0.0.0"
    it_subnet = "10.0.2.0"
    ot_subnet = "10.0.3.0"
    data_subnet = "10.0.1.0"

    # Your code here
    # Rule 1: ICMP traffic is forwarded only between the Sales Department, IT Department, and OT Department subnets or between devices that are on the same subnet.
    if icmp_packet is not None:
      src_ip = str(ipv4_packet.srcip)
      dst_ip = str(ipv4_packet.dstip)
      print ("Source IP: " + src_ip)
      print("Dest IP: " + dst_ip)

      #end_port = None

      if (switch_id == 1): #Packet ended up in Sales Department
        if(not(check_valid_ip(dst_ip, sales_subnet, 24))): # Make sure the dest is intended for hosts inside sales subnet
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else: 
          if dst_ip == "10.0.0.10":
            accept(2) # Forward it to Laptop1
          elif dst_ip == "10.0.0.9":
            accept(3) # Forward it to Printer
          elif dst_ip == "10.0.0.8":
            accept(4) # Forward it to Laptop2
          else:  
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 2): #Packet ended up in OT Department
        if(not(check_valid_ip(dst_ip, ot_subnet, 24))): # Make sure the dest is intended for hosts inside sales subnet
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else:
          if dst_ip == "10.0.3.7":
            accept(2) # Forward it to WS1
          elif dst_ip == "10.0.3.6":
            accept(3) # Forward it to WS2
          else:
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 3): # Packet ended up in IT Department
        if(not(check_valid_ip(dst_ip, it_subnet, 24))):
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else:
          if dst_ip == "10.0.2.4":
            accept(2) # Forward it to WS4
          elif dst_ip == "10.0.2.5":
            accept(3) # Forward it to WS3
          else:
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 4):
        if(not(check_valid_ip(dst_ip, data_subnet, 24))):
          return #Drop the packet if dst is intended for hosts outside of subnet
        else:
          if dst_ip == "10.0.1.1":
            accept(4) #Forward it to server2
          elif dst_ip == "10.0.1.2":
            accept(3) # Forward it to WebServer
          elif dst_ip == "10.0.1.3":
            accept(2) #Forward it to DNSServer
          else:
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 5):
        if (check_valid_ip(dst_ip, sales_subnet, 24)):
          accept(4)
        elif (check_valid_ip(dst_ip, ot_subnet, 24)):
          accept(1)
        elif (check_valid_ip(dst_ip, it_subnet, 24)):
          accept(2)
        elif (check_valid_ip(dst_ip, data_subnet, 24)):
          return
        else:
          return
      else:
        return
      #return #for if icmp_packet is not None:

    # Rule 2: TCP traffic is forwarded only between the Datacenter, IT Department and OT Department subnets or between devices that are on the same subnet.
    elif tcp_packet is not None:
      src_ip = str(ipv4_packet.srcip)
      dst_ip = str(ipv4_packet.dstip)
      if (switch_id == 1): #Hosts in Sales Department can only communicate with each other. 
        if(not(check_valid_ip(dst_ip, sales_subnet, 24))): #Hosts inside subnet can communicate with each other
          return #Drop the packet if dst is intended for hosts outside of subnet
        else:
          if dst_ip == "10.0.0.10":
            accept(2)
          if dst_ip == "10.0.0.9":
            accept(3)
          if dst_ip == "10.0.0.8":
            accept(4)
          else:
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 2): #Packet ended up in OT Department
        if(not(check_valid_ip(dst_ip, ot_subnet, 24))): # Make sure the dest is intended for hosts inside sales subnet
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else:
          if dst_ip == "10.0.3.7":
            accept(2) # Forward it to WS1
          elif dst_ip == "10.0.3.6":
            accept(3) # Forward it to WS2
          else:
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 3): # Packet ended up in IT Department
        if(not(check_valid_ip(dst_ip, it_subnet, 24))):
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else:
          if dst_ip == "10.0.2.4":
            accept(2) # Forward it to WS4
          elif dst_ip == "10.0.2.5":
            accept(3) # Forward it to WS3
          else:
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 4):
        if(not(check_valid_ip(dst_ip, data_subnet, 24))): 
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else: 
          if dst_ip == "10.0.1.1":
            accept(4) # Forward packet Server2
          elif dst_ip == "10.0.1.2":
            accept(3) # Foward packet to WebServer
          elif dst_ip == "10.0.1.3":
            accept(2) # Forward Packet to DNSserver
          else:  
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 5):
        if (check_valid_ip(dst_ip, sales_subnet, 24)):
          return
        elif (check_valid_ip(dst_ip, ot_subnet, 24)):
          accept(1)
        elif (check_valid_ip(dst_ip, it_subnet, 24)):
          accept(2)
        elif (check_valid_ip(dst_ip, data_subnet, 24)):
          accept(3)
        else:
          return
      else:
        return

    # Rule 3: UDP traffic is forwarded only between the Sales Department and Datacenter subnets or between devices that are on the same subnet.
    elif udp_packet is not None:
      src_ip = str(ipv4_packet.srcip)
      dst_ip = str(ipv4_packet.dstip)

      if (switch_id == 1): #Packet ended up in Sales Department
        if(not(check_valid_ip(dst_ip, sales_subnet, 24))): # Make sure the dest is intended for hosts inside sales subnet
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else: 
          if dst_ip == "10.0.0.10":
            accept(2) # Forward it to Laptop1
          elif dst_ip == "10.0.0.9":
            accept(3) # Forward it to Printer
          elif dst_ip == "10.0.0.8":
            accept(4) # Forward it to Laptop2
          else:  
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 2): #Packet ended up in OT Department
        if(not(check_valid_ip(dst_ip, ot_subnet, 24))):
          return #Drop the packet if dst is intended for hosts outside of subnet
        else:
          if dst_ip == "10.0.3.7":
            accept(2)
          elif dst_ip == "10.0.3.6":
            accept(3)
      elif(switch_id == 2): #Packet ended up in IT Department
        if(not(check_valid_ip(dst_ip, it_subnet, 24))):
          return #Drop the packet if dst is intended for hosts outside of subnet
        else:
          if dst_ip == "10.0.2.4":
            accept(2)
          elif dst_ip == "10.0.2.5":
            accept(3)
      elif(switch_id == 4):
        if(not(check_valid_ip(dst_ip, data_subnet, 24))): 
          accept(1) # Forward packet to CoreSwitch since it's not for hosts in subnet
        else: 
          if dst_ip == "10.0.1.1":
            accept(4) # Forward packet Server2
          elif dst_ip == "10.0.1.2":
            accept(3) # Foward packet to WebServer
          elif dst_ip == "10.0.1.3":
            accept(2) # Forward Packet to DNSserver
          else:  
            print"IP may be in the subnet but host doesn't exist"
            return
      elif(switch_id == 5):
        if (check_valid_ip(dst_ip, sales_subnet, 24)):
          accept(4)
        elif (check_valid_ip(dst_ip, ot_subnet, 24)):
          return
        elif (check_valid_ip(dst_ip, it_subnet, 24)):
          return
        elif (check_valid_ip(dst_ip, data_subnet, 24)):
          accept(3)
        else:
          return
      else:
        return

    

    #pass

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_routing(packet, packet_in, event.port, event.dpid)



def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Routing(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)