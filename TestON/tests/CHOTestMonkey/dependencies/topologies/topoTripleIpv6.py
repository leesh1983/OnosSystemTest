#!/usr/bin/python

"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Host, RemoteController
from mininet.node import Node
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.node import ( UserSwitch, OVSSwitch, IVSSwitch )


class dualStackHost( Host ):

    def config( self, v6Addr='1000::1/64', **params ):
        r = super( Host, self ).config( **params )
        intf = self.defaultIntf()
        self.cmd( 'ip -6 addr add %s dev %s' % ( v6Addr, intf ) )
        return r


class tripleTopo( Topo ):

    def __init__( self, **opts ):
        "Create a topology."

        # Initialize Topology
        Topo.__init__( self, **opts )

        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )

        # ... and now hosts
        s1_host = self.addHost( 'h1', ip='10.1.0.1/24', cls=dualStackHost, v6Addr='1000::1/64' )
        s2_host = self.addHost( 'h2', ip='10.1.0.2/24', cls=dualStackHost, v6Addr='1000::2/64' )
        s3_host = self.addHost( 'h3', ip='10.1.0.3/24', cls=dualStackHost, v6Addr='1000::3/64' )

        # add edges between switch and corresponding host
        self.addLink( s1, s1_host )
        self.addLink( s2, s2_host )
        self.addLink( s3, s3_host )
        self.addLink( s1, s2 )
        self.addLink( s1, s3 )
        self.addLink( s2, s3 )

topos = { 'triple': ( lambda: tripleTopo() ) }

# HERE THE CODE DEFINITION OF THE TOPOLOGY ENDS


def setupNetwork():
    "Create network"
    topo = tripleTopo()
    # if controller_ip == '':
    # controller_ip = '10.0.2.2';
    #    controller_ip = '127.0.0.1';
    network = Mininet( topo=topo, switch=OVSSwitch, autoSetMacs=True, controller=None )
    network.start()
    CLI( network )
    network.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    # setLogLevel( 'debug' )
    setupNetwork()
