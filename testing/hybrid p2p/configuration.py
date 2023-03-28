# Pure P2P:
# h1: server
# h2, h3: peers
# h4: the peer who initiate the connection

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.cli import CLI
import time

class MyTopo( Topo ):  
    def __init__( self ):

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        Host1 = self.addHost( 'h1' )
        Host2 = self.addHost( 'h2' )
        Host3 = self.addHost( 'h3' )
        Host4 = self.addHost( 'h4' )
        Switch1 = self.addSwitch('s1')
        Switch2 = self.addSwitch('s2')
        # Add links
        self.addLink( Host1, Switch1, cls=TCLink, bw=10)
        self.addLink( Host2, Switch1, cls=TCLink, bw=8)
        self.addLink( Host3, Switch2, cls=TCLink, bw=25)
        self.addLink( Host4, Switch2, cls=TCLink, bw=20)
        self.addLink( Switch1, Switch2 )

topo = MyTopo()
net = Mininet(topo=topo, controller=OVSController)
net.start()
h1 = net.get('h1')
h2 = net.get('h2')
h3 = net.get('h3')
h4 = net.get('h4')
print h1.sendCmd('python server.py')
print h2.sendCmd('python peer.py')
print h3.sendCmd('python peer.py')
time.sleep(5)
print h4.cmd('python query.py')

net.stop()
