'''Experiment profile for cloudlab experiments'''

import geni.portal as portal
import geni.rspec.pg as pg


''' Parameters '''

# Describe the parameter(s) this profile script can accept.
#portal.context.defineParameter( "N", "Number of VMs", portal.ParameterType.INTEGER, 4)
portal.context.defineParameter( "SITES", "Number of Sites", portal.ParameterType.INTEGER, 2)

# Retrieve the values the user specifies during instantiation.
params = portal.context.bindParameters()


''' Network Configuration '''

# Size and naming convention configuration
N = 64 # CONFIGURE
M = 2 * N
SITES = params.SITES
BHOST = 'bulletin'
node_prefix = 'node'
NPORT = '50050'

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Create an array for interfaces
ifaces = []


''' Node Setup '''

nodes = []
for n in range(0, M):

    # Create node
    node = request.RawPC(node_prefix + str(n))

    # Node script directories
    node_startup = "/local/repository/node.sh"
    node_output = "/local/repository/startup_output.txt"

    # Add node startup script
    node.addService(pg.Execute(shell="sh", command=str(node_startup) + " " + str(n) + ' ' + str(NPORT) + " >> " + node_output))

    # Set node site
    node.Site("Site" + str(n % SITES + 1))

    node.hardware_type = 'm510'

    # Node networking
    iface = node.addInterface("eth1")
    iface.addAddress(pg.IPv4Address("192.168.1." + str(n + 1), "255.255.255.0"))
    ifaces.append(iface)

    nodes += [node]


''' Bulletin Setup '''

# Create bulletin
bulletin = request.RawPC(BHOST)

bulletin.hardware_type = 'm510'

# Bulletin script direectories
bulletin_startup = "/local/repository/bulletin.sh"
bulletin_output = "/local/repository/startup_output.txt"

# Add bulletin startup script
bulletin.addService(pg.Execute(shell="sh", command=str(bulletin_startup)  + " >> " + bulletin_output))

# Set bulletin site
bulletin.Site("Site1")

# Bulletin networking
iface = bulletin.addInterface("eth1")
iface.addAddress(pg.IPv4Address("192.168.1.254", "255.255.255.0"))
ifaces.append(iface)


''' Networking Setup '''

#request.Link(members=(nodes + [bulletin]))

lan = request.LAN("lan")
lan.bandwidth=100000

for iface in ifaces:
    lan.addInterface(iface)


''' Print Resulting RSpec '''

pc.printRequestRSpec(request)
