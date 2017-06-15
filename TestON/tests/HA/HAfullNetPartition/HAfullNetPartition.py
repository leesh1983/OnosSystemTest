"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Description: This test is to determine if ONOS can handle
             a full network partion

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign devices to controllers
CASE21: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE61: The Failure inducing case.
CASE62: The Failure recovery case.
CASE7: Check state after control plane failure
CASE8: Compare topo
CASE9: Link s3-s28 down
CASE10: Link s3-s28 up
CASE11: Switch down
CASE12: Switch up
CASE13: Clean up
CASE14: start election app on all onos nodes
CASE15: Check that Leadership Election is still functional
CASE16: Install Distributed Primitives app
CASE17: Check for basic functionality with distributed primitives
"""
class HAfullNetPartition:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-uninstall
        start mininet
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start tcpdump
        """
        import imp
        import pexpect
        import time
        import json
        main.log.info( "ONOS HA test: Partition ONOS nodes into two sub-clusters - " +
                         "initialization" )
        # set global variables
        # These are for csv plotting in jenkins
        main.HAlabels = []
        main.HAdata = []
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        main.testSetUp.envSetupDescription()
        try:
            from tests.HA.dependencies.HA import HA
            main.HA = HA()
            # load some variables from the params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'appString' ]
            main.numCtrls = int( main.params[ 'num_controllers' ] )
            if main.ONOSbench.maxNodes and\
                        main.ONOSbench.maxNodes < main.numCtrls:
                main.numCtrls = int( main.ONOSbench.maxNodes )
            main.maxNodes = main.numCtrls
            stepResult = main.testSetUp.envSetup( hasNode=True )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.HA.generateGraph( "HAfullNetPartition" )

        main.testSetUp.ONOSSetUp( main.Mininet1, cellName=cellName, removeLog=True,
                                 extraApply=main.HA.customizeOnosGenPartitions,
                                 extraClean=main.HA.cleanUpGenPartition )

        main.HA.initialSetUp()


    def CASE2( self, main ):
        """
        Assign devices to controllers
        """
        main.HA.assignDevices( main )

    def CASE21( self, main ):
        """
        Assign mastership to controllers
        """
        main.HA.assignMastership( main )

    def CASE3( self, main ):
        """
        Assign intents
        """
        main.HA.assignIntents( main )

    def CASE4( self, main ):
        """
        Ping across added host intents
        """
        main.HA.pingAcrossHostIntent( main )

    def CASE5( self, main ):
        """
        Reading state of ONOS
        """
        main.HA.readingState( main )

    def CASE61( self, main ):
        """
        The Failure case.
        """
        import math
        assert main.numCtrls, "main.numCtrls not defined"
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        assert main.CLIs, "main.CLIs not defined"
        assert main.nodes, "main.nodes not defined"
        main.case( "Partition ONOS nodes into two distinct partitions" )

        main.step( "Checking ONOS Logs for errors" )
        for node in main.nodes:
            main.log.debug( "Checking logs for errors on " + node.name + ":" )
            main.log.warn( main.ONOSbench.checkLogs( node.ip_address ) )

        main.log.debug( main.CLIs[ 0 ].roles( jsonFormat=False ) )

        n = len( main.nodes )  # Number of nodes
        p = ( ( n + 1 ) / 2 ) + 1  # Number of partitions
        main.partition = [ 0 ]  # ONOS node to partition, listed by index in main.nodes
        if n > 3:
            main.partition.append( p - 1 )
            # NOTE: This only works for cluster sizes of 3,5, or 7.

        main.step( "Partitioning ONOS nodes" )
        nodeList = [ str( i + 1 ) for i in main.partition ]
        main.log.info( "Nodes to be partitioned: " + str( nodeList ) )
        partitionResults = main.TRUE
        for i in range( 0, n ):
            this = main.nodes[ i ]
            if i not in main.partition:
                for j in main.partition:
                    foe = main.nodes[ j ]
                    main.log.warn( "Setting IP Tables rule from {} to {}. ".format( this.ip_address, foe.ip_address ) )
                    #CMD HERE
                    cmdStr = "sudo iptables -A {} -d {} -s {} -j DROP".format( "INPUT", this.ip_address, foe.ip_address )
                    this.handle.sendline( cmdStr )
                    this.handle.expect( "\$" )
                    main.log.debug( this.handle.before )
            else:
                for j in range( 0, n ):
                    if j not in main.partition:
                        foe = main.nodes[ j ]
                        main.log.warn( "Setting IP Tables rule from {} to {}. ".format( this.ip_address, foe.ip_address ) )
                        #CMD HERE
                        cmdStr = "sudo iptables -A {} -d {} -s {} -j DROP".format( "INPUT", this.ip_address, foe.ip_address )
                        this.handle.sendline( cmdStr )
                        this.handle.expect( "\$" )
                        main.log.debug( this.handle.before )
                main.activeNodes.remove( i )
        # NOTE: When dynamic clustering is finished, we need to start checking
        #       main.partion nodes still work when partitioned
        utilities.assert_equals( expect=main.TRUE, actual=partitionResults,
                                 onpass="Firewall rules set successfully",
                                 onfail="Error setting firewall rules" )

        main.step( "Sleeping 60 seconds" )
        time.sleep( 60 )

    def CASE62( self, main ):
        """
        Healing Partition
        """
        import time
        assert main.numCtrls, "main.numCtrls not defined"
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        assert main.CLIs, "main.CLIs not defined"
        assert main.nodes, "main.nodes not defined"
        assert main.partition, "main.partition not defined"
        main.case( "Healing Partition" )

        main.step( "Deleteing firewall rules" )
        healResults = main.TRUE
        for node in main.nodes:
            cmdStr = "sudo iptables -F"
            node.handle.sendline( cmdStr )
            node.handle.expect( "\$" )
            main.log.debug( node.handle.before )
        utilities.assert_equals( expect=main.TRUE, actual=healResults,
                                 onpass="Firewall rules removed",
                                 onfail="Error removing firewall rules" )

        for node in main.partition:
            main.activeNodes.append( node )
        main.activeNodes.sort()
        try:
            assert list( set( main.activeNodes ) ) == main.activeNodes,\
                   "List of active nodes has duplicates, this likely indicates something was run out of order"
        except AssertionError:
            main.log.exception( "" )
            main.cleanup()
            main.exit()

        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( main.HA.nodesCheck,
                                       False,
                                       args=[ main.activeNodes ],
                                       sleep=15,
                                       attempts=5 )

        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )

        if not nodeResults:
            for i in main.activeNodes:
                cli = main.CLIs[ i ]
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    cli.name,
                    cli.sendline( "scr:list | grep -v ACTIVE" ) ) )
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanup()
            main.exit()

    def CASE7( self, main ):
        """
        Check state after ONOS failure
        """

        main.HA.checkStateAfterONOS( main, afterWhich=0 )

        main.step( "Leadership Election is still functional" )
        # Test of LeadershipElection
        leaderList = []

        partitioned = []
        for i in main.partition:
            partitioned.append( main.nodes[ i ].ip_address )
        leaderResult = main.TRUE

        for i in main.activeNodes:
            cli = main.CLIs[ i ]
            leaderN = cli.electionTestLeader()
            leaderList.append( leaderN )
            if leaderN == main.FALSE:
                # error in response
                main.log.error( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leaderN is None:
                main.log.error( cli.name +
                                 " shows no leader for the election-app was" +
                                 " elected after the old one died" )
                leaderResult = main.FALSE
            elif leaderN in partitioned:
                main.log.error( cli.name + " shows " + str( leaderN ) +
                                 " as leader for the election-app, but it " +
                                 "was partitioned" )
                leaderResult = main.FALSE
        if len( set( leaderList ) ) != 1:
            leaderResult = main.FALSE
            main.log.error(
                "Inconsistent view of leader for the election test app" )
            # TODO: print the list
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

    def CASE8( self, main ):
        """
        Compare topo
        """
        main.HA.compareTopo( main )

    def CASE9( self, main ):
        """
        Link s3-s28 down
        """
        main.HA.linkDown( main )

    def CASE10( self, main ):
        """
        Link s3-s28 up
        """
        main.HA.linkUp( main )

    def CASE11( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        main.HA.switchDown( main )

    def CASE12( self, main ):
        """
        Switch Up
        """
        # NOTE: You should probably run a topology check after this
        main.HA.switchUp( main )

    def CASE13( self, main ):
        """
        Clean up
        """
        main.HA.cleanUp( main )

    def CASE14( self, main ):
        """
        start election app on all onos nodes
        """
        main.HA.startElectionApp( main )

    def CASE15( self, main ):
        """
        Check that Leadership Election is still functional
            15.1 Run election on each node
            15.2 Check that each node has the same leaders and candidates
            15.3 Find current leader and withdraw
            15.4 Check that a new node was elected leader
            15.5 Check that that new leader was the candidate of old leader
            15.6 Run for election on old leader
            15.7 Check that oldLeader is a candidate, and leader if only 1 node
            15.8 Make sure that the old leader was added to the candidate list

            old and new variable prefixes refer to data from before vs after
                withdrawl and later before withdrawl vs after re-election
        """
        main.HA.isElectionFunctional( main )

    def CASE16( self, main ):
        """
        Install Distributed Primitives app
        """
        main.HA.installDistributedPrimitiveApp( main )

    def CASE17( self, main ):
        """
        Check for basic functionality with distributed primitives
        """
        main.HA.checkDistPrimitivesFunc( main )
