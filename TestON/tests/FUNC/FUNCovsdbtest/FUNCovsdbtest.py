"""
Copyright 2015 Open Networking Foundation ( ONF )

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
"""
Description: This test is to check onos set configuration and flows with ovsdb connection.

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Test ovsdb connection and tearDown
CASE3: Test default br-int configuration and vxlan port
CASE4: Test default openflow configuration
CASE5: Test default flows
CASE6: Configure Network Subnet Port
CASE7: Test host go online and ping each other
CASE8: Clear ovs configuration and host configuration
zhanghaoyu7@huawei.com
"""
import os


class FUNCovsdbtest:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        Construct test variables
        Safety check, kill all ONOS processes before setup
        NOTE: temporary - onos-remove-raft-logs
        Create ONOS package
        Install ONOS package
        start cli sessions
        start ovsdb
        start vtn apps
        """
        import os
        import time
        main.log.info( "ONOS Single node start ovsdb test - initialization" )
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE

        try:
            # load some variables from the params file
            main.step( "Constructing test variables" )
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            stepResult = main.testSetUp.envSetup()

        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

        cliResults = main.testSetUp.ONOSSetUp( main.Cluster, cellName=cellName,
                                               mininetIp=main.OVSDB1, removeLog=True )

        if cliResults == main.FALSE:
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanAndExit()

        main.step( "App Ids check" )
        appCheck = main.Cluster.active( 0 ).CLI.appToIDCheck()

        if appCheck != main.TRUE:
            main.log.warn( main.Cluster.active( 0 ).CLI.apps() )
            main.log.warn( main.Cluster.active( 0 ).CLI.appIDs() )

        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

        main.step( "Install onos-ovsdb" )
        installResults = main.Cluster.active( 0 ).CLI.activateApp( "org.onosproject.ovsdb" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-ovsdatabase successful",
                                 onfail="Install onos-ovsdatabase failed" )

        main.step( "Install onos-app-vtn" )
        installResults = main.Cluster.active( 0 ).CLI.activateApp( "org.onosproject.vtn" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-vtn successful",
                                 onfail="Install onos-app-vtn failed" )

    def CASE2( self, main ):
        """
        Test ovsdb connection and teardown
        """
        import os
        import re

        main.case( "Test ovsdb connection and teardown" )
        main.caseExplanation = "Test ovsdb connection create and delete" +\
                                " over ovsdb node and onos node "

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "Set ovsdb node manager" )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Set ovsdb node manager sucess",
                                 onfail="Set ovsdb node manager failed" )

        main.step( "Check ovsdb node manager is " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check ovsdb node manager is " + str( response ),
                                 onfail="Check ovsdb node manager failed" )

        main.step( "Delete ovsdb node manager" )
        deleteResult = main.OVSDB1.delManager( delaytime=delaytime )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node delete manager sucess",
                                 onfail="ovsdb node delete manager failed" )

        main.step( "Check ovsdb node delete manager " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if not re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check ovsdb node delete manager sucess",
                                 onfail="Check ovsdb node delete manager failed" )

    def CASE3( self, main ):
        """
        Test default br-int configuration and vxlan port
        """
        import re
        import os

        main.case( "Test default br-int configuration and vxlan port" )
        main.caseExplanation = "onos create default br-int bridge and" +\
                                " vxlan port on the ovsdb node"

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]
        OVSDB1Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip1' ] )
        OVSDB2Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip2' ] )

        main.step( "ovsdb node 1 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " failed" )

        main.step( "ovsdb node 2 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB2.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 set ovs manager to  to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 2 set ovs manager to  to " +
                                  str( ctrlip ) + " failed" )

        main.step( "Check ovsdb node 1 manager is " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 manager is " + str( response ),
                                 onfail="ovsdb node 1 manager check failed" )

        main.step( "Check ovsdb node 2 manager is " + str( ctrlip ) )
        response = main.OVSDB2.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 manager is " + str( response ),
                                 onfail="ovsdb node 2 manager check failed" )

        main.step( "Check default br-int bridge on ovsdb node " + str( OVSDB1Ip ) )
        response = main.OVSDB1.listBr()
        if re.search( "br-int", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default bridge on the node 1 sucess",
                                 onfail="onos add default bridge on the node 1 failed" )

        main.step( "Check default br-int bridge on ovsdb node " + str( OVSDB2Ip ) )
        response = main.OVSDB2.listBr()
        if re.search( "br-int", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default bridge on the node 2 sucess",
                                 onfail="onos add default bridge on the node 2 failed" )

        main.step( "Check default vxlan port on ovsdb node " + str( OVSDB1Ip ) )
        response = main.OVSDB1.listPorts( "br-int" )
        if re.search( "vxlan", response ) and re.search( str( OVSDB2Ip ), response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default vxlan port on the node 1 sucess",
                                 onfail="onos add default vxlan port on the node 1 failed" )

        main.step( "Check default vxlan port on ovsdb node " + str( OVSDB2Ip ) )
        response = main.OVSDB2.listPorts( "br-int" )
        if re.search( "vxlan", response ) and re.search( str( OVSDB1Ip ), response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default vxlan port on the node 2 sucess",
                                 onfail="onos add default vxlan port on the node 2 failed" )

    def CASE4( self, main ):
        """
        Test default openflow configuration
        """
        import re
        import os

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "ovsdb node 1 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " failed" )

        main.step( "ovsdb node 2 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB2.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 set ovs manager to  to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 2 set ovs manager to  to " +
                                  str( ctrlip ) + " failed" )

        main.step( "Check ovsdb node 1 manager is " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 manager is " + str( response ),
                                 onfail="ovsdb node 1 manager check failed\n" +
                                 str( main.OVSDB1.show() ) )

        main.step( "Check ovsdb node 2 manager is " + str( ctrlip ) )
        response = main.OVSDB2.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 manager is " + str( response ),
                                 onfail="ovsdb node 2 manager check failed\n" +
                                 str( main.OVSDB2.show() ) )

        main.step( "Check ovsdb node 1 bridge br-int controller set to " + str( ctrlip ) )
        response = main.OVSDB1.getController( "br-int" )
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check ovsdb node 1 bridge br-int controller set to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="Check ovsdb node 1 bridge br-int controller set to " +
                                  str( ctrlip ) + " failed\n" + str( main.OVSDB1.show() ) )

        main.step( "Check ovsdb node 2 bridge br-int controller set to  " + str( ctrlip ) )
        response = main.OVSDB2.getController( "br-int" )
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check ovsdb node 2 bridge br-int controller set to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="Check ovsdb node 2 bridge br-int controller set to " +
                                  str( ctrlip ) + " failed\n" + str( main.OVSDB2.show() ) )

        main.step( "Check onoscli devices have ovs " + str( OVSDB1Ip ) )
        response = main.Cluster.active( 0 ).CLI.devices()
        if re.search( OVSDB1Ip, response ) and not re.search( "false", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check onoscli devices have ovs " + str( OVSDB1Ip ) + " sucess",
                                 onfail="Check onoscli devices have ovs " + str( OVSDB1Ip ) + " failed" )

        main.step( "Check onoscli devices have ovs " + str( OVSDB2Ip ) )
        response = main.Cluster.active( 0 ).CLI.devices()
        if re.search( OVSDB2Ip, response ) and not re.search( "false", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check onoscli devices have ovs " + str( OVSDB2Ip ) + " sucess",
                                 onfail="Check onoscli devices have ovs " + str( OVSDB2Ip ) + " failed" )

    def CASE5( self, main ):
        """
        Test default flows
        """
        import re
        import os

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "ovsdb node 1 set ovs manager to onos" )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " failed" )

        main.step( "Check ovsdb node 1 manager is " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 manager is " + str( response ),
                                 onfail="ovsdb node 1 manager check failed" )

        main.step( "Check ovsdb node 1 bridge br-int default flows on " + str( OVSDB1Ip ) )
        response = main.OVSDB1.dumpFlows( sw="br-int", protocols="OpenFlow13" )
        if re.search( "actions=CONTROLLER", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully set default flows " + str( ctrlip ),
                                 onfail="Failed to set default flows " + str( ctrlip ) )

    def CASE6( self, main ):
        """
        Configure Network Subnet Port
        """
        import os

        try:
            from tests.FUNC.FUNCovsdbtest.dependencies.Nbdata import NetworkData
            from tests.FUNC.FUNCovsdbtest.dependencies.Nbdata import SubnetData
            from tests.FUNC.FUNCovsdbtest.dependencies.Nbdata import VirtualPortData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanAndExit()

        main.log.info( "Configure Network Subnet Port Start" )
        main.case( "Configure Network Subnet Port" )
        main.caseExplanation = "Configure Network Subnet Port " +\
                                "Verify post is OK"

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        httpport = main.params[ 'HTTP' ][ 'port' ]
        path = main.params[ 'HTTP' ][ 'path' ]

        main.step( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        subnet.start = "10.0.0.1"
        subnet.end = "10.0.0.254"
        subnet.cidr = "10.0.0.0/24"
        port1 = VirtualPortData()
        port1.id = "00000000-0000-0000-0000-000000000001"
        port1.subnet_id = subnet.id
        port1.tenant_id = network.tenant_id
        port1.network_id = network.id
        port1.macAddress = "00:00:00:00:00:01"
        port1.ip_address = "10.0.0.1"
        port2 = VirtualPortData()
        port2.id = "00000000-0000-0000-0000-000000000002"
        port2.subnet_id = subnet.id
        port2.tenant_id = network.tenant_id
        port2.network_id = network.id
        port2.macAddress = "00:00:00:00:00:02"
        port2.ip_address = "10.0.0.2"

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        port1postdata = port1.DictoJson()
        port2postdata = port2.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.Cluster.active( 0 ).REST.send( 'networks/', ctrlip, httpport, path,
                                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.Cluster.active( 0 ).REST.send( 'subnets/', ctrlip, httpport, path,
                                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port1 Data via HTTP" )
        Poststatus, result = main.Cluster.active( 0 ).REST.send( 'ports/', ctrlip, httpport, path,
                                                                 'POST', None, port1postdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port2 Data via HTTP" )
        Poststatus, result = main.Cluster.active( 0 ).REST.send( 'ports/', ctrlip, httpport, path,
                                                                 'POST', None, port2postdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

    def CASE7( self, main ):
        """
        Test host go online and ping each other
        """
        import re
        import os

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "ovsdb node 1 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 1 set ovs manager to  to " +
                                  str( ctrlip ) + " failed" )

        main.step( "ovsdb node 2 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB2.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 set ovs manager to " +
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 2 set ovs manager to " +
                                  str( ctrlip ) + " failed" )

        main.step( "Create host1 on node 1 " + str( OVSDB1Ip ) )
        stepResult = main.OVSDB1.createHost( hostname="host1" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create host1 on node 1 " + str( OVSDB1Ip ) + " sucess",
                                 onfail="Create host1 on node 1 " + str( OVSDB1Ip ) + " failed" )

        main.step( "Create host2 on node 2 " + str( OVSDB2Ip ) )
        stepResult = main.OVSDB2.createHost( hostname="host2" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create host2 on node 2 " + str( OVSDB2Ip ) + " sucess",
                                 onfail="Create host2 on node 2 " + str( OVSDB2Ip ) + " failed" )

        main.step( "Create port on host1 on the node " + str( OVSDB1Ip ) )
        stepResult = main.OVSDB1.createHostport( hostname="host1", hostport="host1-eth0", hostportmac="000000000001" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create port on host1 on the node " + str( OVSDB1Ip ) + " sucess",
                                 onfail="Create port on host1 on the node " + str( OVSDB1Ip ) + " failed" )

        main.step( "Create port on host2 on the node " + str( OVSDB2Ip ) )
        stepResult = main.OVSDB2.createHostport( hostname="host2", hostport="host2-eth0", hostportmac="000000000002" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create port on host1 on the node " + str( OVSDB2Ip ) + " sucess",
                                 onfail="Create port on host1 on the node " + str( OVSDB2Ip ) + " failed" )

        main.step( "Add port to ovs br-int and host go-online on the node " + str( OVSDB1Ip ) )
        stepResult = main.OVSDB1.addPortToOvs( ovsname="br-int", ifaceId="00000000-0000-0000-0000-000000000001",
                                               attachedMac="00:00:00:00:00:01", vmuuid="10000000-0000-0000-0000-000000000001" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Add port to ovs br-int and host go-online on the node " +
                                  str( OVSDB1Ip ) + " sucess",
                                 onfail="Add port to ovs br-int and host go-online on the node " +
                                  str( OVSDB1Ip ) + " failed" )

        main.step( "Add port to ovs br-int and host go-online on the node " + str( OVSDB2Ip ) )
        stepResult = main.OVSDB2.addPortToOvs( ovsname="br-int", ifaceId="00000000-0000-0000-0000-000000000002",
                                               attachedMac="00:00:00:00:00:02", vmuuid="10000000-0000-0000-0000-000000000001" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Add port to ovs br-int and host go-online on the node " +
                                  str( OVSDB2Ip ) + " sucess",
                                 onfail="Add port to ovs br-int and host go-online on the node " +
                                  str( OVSDB2Ip ) + " failed" )

        main.step( "Check onos set host flows on the node " + str( OVSDB1Ip ) )
        response = main.OVSDB1.dumpFlows( sw="br-int", protocols="OpenFlow13" )
        if re.search( "00:00:00:00:00:01", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check onos set host flows on the node " +
                                  str( OVSDB1Ip ) + " sucess",
                                 onfail="Check onos set host flows on the node " +
                                  str( OVSDB1Ip ) + " failed" )

        main.step( "Check onos set host flows on the node " + str( OVSDB2Ip ) )
        response = main.OVSDB2.dumpFlows( sw="br-int", protocols="OpenFlow13" )
        if re.search( "00:00:00:00:00:02", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check onos set host flows on the node " +
                                  str( OVSDB2Ip ) + " sucess",
                                 onfail="Check onos set host flows on the node " +
                                  str( OVSDB2Ip ) + " failed" )

        main.step( "Check hosts can ping each other" )
        main.OVSDB1.setHostportIp( hostname="host1", hostport1="host1-eth0", ip="10.0.0.1" )
        main.OVSDB2.setHostportIp( hostname="host2", hostport1="host2-eth0", ip="10.0.0.2" )
        pingResult1 = main.OVSDB1.hostPing( src="10.0.0.1", hostname="host1", target="10.0.0.2" )
        pingResult2 = main.OVSDB2.hostPing( src="10.0.0.2", hostname="host2", target="10.0.0.1" )
        stepResult = pingResult1 and pingResult2
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully host go online and ping each other,controller is " +
                                        str( ctrlip ),
                                 onfail="Failed to host go online and ping each other,controller is " +
                                        str( ctrlip ) )

    def CASE8( self, main ):
        """
        Clear ovs configuration and host configuration
        """
        import re
        import os

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        OVSDB1Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip1' ] )
        OVSDB2Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip2' ] )
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "Delete ovsdb node 1 manager" )
        deleteResult = main.OVSDB1.delManager( delaytime=delaytime )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 delete manager sucess",
                                 onfail="ovsdb node 1 delete manager failed" )

        main.step( "Delete ovsdb node 2 manager" )
        deleteResult = main.OVSDB2.delManager( delaytime=delaytime )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 delete manager sucess",
                                 onfail="ovsdb node 2 delete manager failed" )

        main.step( "Delete ovsdb node 1 bridge br-int" )
        deleteResult = main.OVSDB1.delBr( sw="br-int" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ovsdb node 1 bridge br-int sucess",
                                 onfail="Delete ovsdb node 1 bridge br-int failed" )

        main.step( "Delete ovsdb node 2 bridge br-int" )
        deleteResult = main.OVSDB2.delBr( sw="br-int" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ovsdb node 2 bridge br-int sucess",
                                 onfail="Delete ovsdb node 2 bridge br-int failed" )

        main.step( "Delete ip netns host on the ovsdb node 1" )
        deleteResult = main.OVSDB1.delHost( hostname="host1" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ip netns host on the ovsdb node 1 sucess",
                                 onfail="Delete ip netns host on the ovsdb node 1 failed" )

        main.step( "Delete ip netns host on the ovsdb node 2" )
        deleteResult = main.OVSDB2.delHost( hostname="host2" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ip netns host on the ovsdb node 2 sucess",
                                 onfail="Delete ip netns host on the ovsdb node 2 failed" )

        main.step( "Check onoscli devices openflow session is false " + str( OVSDB1Ip ) )
        response = main.Cluster.active( 0 ).CLI.devices()
        if re.search( OVSDB1Ip, response ) and not re.search( "true", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check openflow session is false " + str( OVSDB1Ip ) + " sucess",
                                 onfail="Check openflow session is false " + str( OVSDB1Ip ) + " failed" )

        main.step( "Check onoscli devices have ovs " + str( OVSDB2Ip ) )
        response = main.Cluster.active( 0 ).CLI.devices()
        if re.search( OVSDB2Ip, response ) and not re.search( "true", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check openflow session is false " + str( OVSDB2Ip ) + " sucess",
                                 onfail="Check openflow session is false " + str( OVSDB2Ip ) + " failed" )
