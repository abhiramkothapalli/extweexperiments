'''Experiment profile for cloudlab experiments'''

import geni.portal as portal
import geni.rspec.pg as pg

N = 2 # CONFIGURE
BHOST = 'bulletin'

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

M = 2 * N

''' Node Creation '''

# Create Nodes
nodes = []
for n in range(0, M):
    node = request.XenVM('node' + str(n))
    nodes += [node]

bulletin = request.XenVM(BHOST)


''' Networking '''


#request.Link(members=(nodes + [bulletin]))


''' VM SETUP '''

# Node Execute Scripts
ifaces = []
for n in range(0, M):

    node = nodes[n]

    output = "/local/repository/startup_output.txt"

    nodehost = 'node' + str(n)
    NPORT = '50050'

    i = 0
    if n >= N:
        i = 1
    j = n % N

    node.addService(pg.Execute(shell="sh", command="/local/repository/node.sh " + str(n) + ' ' + str(NPORT) + " >> " + output))
    node.Site("Site" + str(n % 2))
    ifc = node.addInterface("eth1")
    # Specify the IPv4 address
    ifc.addAddress(pg.IPv4Address("192.168.1." + str(n + 1), "255.255.255.0"))
    ifaces.append(ifc)


# Bulletin Execute Scripts
bulletin.addService(pg.Execute(shell="sh", command="/local/repository/bulletin.sh"  + " >> " + output))
bulletin.Site("Site1")
ifc = bulletin.addInterface("eth1")
# Specify the IPv4 address
ifc.addAddress(pg.IPv4Address("192.168.1.254", "255.255.255.0"))
ifaces.append(ifc)

lan = request.LAN("lan")
lan.bandwidth=100000

for ifc in ifaces:
    lan.addInterface(ifc)

''' Print Resulting RSpec '''

pc.printRequestRSpec(request)
