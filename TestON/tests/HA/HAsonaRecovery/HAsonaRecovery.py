class HAsonaRecovery:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
            Setup and test env
        """
        from tests.dependencies.ONOSSetup import ONOSSetup
        main.testSetUp = ONOSSetup()

        main.log.info( "SONA clustering test: Restart all ONOS nodes - " +
                       "initialization" )
        # These are for csv plotting in jenkins
        main.HAlabels = []
        main.HAdata = []
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        try:
            from tests.HA.dependencies.HA import HA
            main.HA = HA()
            # load some variables from the params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'appString' ]
            stepResult = main.testSetUp.envSetup( includeGitPull=False, includeCaseDesc=False )
        except Exception as e:
            main.testSetUp.envSetupException( e )

        main.testSetUp.ONOSSetUp( main.Cluster, cellName=cellName, removeLog=True, skipPack=True,
                                  extraApply=None )
        main.HA.initialSetUp()
        clusterNode = main.Cluster.next()
        main.ONOSbench.setOnosNetCfg(hostIp=clusterNode.ipAddress, cfgFile=main.params[ 'networkCfg' ].get( 'path' ))
        clusterNode.openstackSyncRules()
        clusterNode.openstackSyncStates()

        main.step( 'Set logging levels' )
        logging = True
        try:
            logs = main.params.get( 'ONOS_Logging', False )
            if logs:
                for namespace, level in logs.items():
                    for ctrl in main.Cluster.active():
                        ctrl.CLI.logSet( level, namespace )
        except AttributeError:
            logging = False
        utilities.assert_equals( expect=True, actual=logging,
                                 onpass="Set log levels",
                                 onfail="Failed to set log levels" )

    def CASE2( self, main):
        import time
        """
            ONOS Recovery Test
        """
        main.case( "ONOS Recovery test" )

        main.step( "Tempest configure" )
        main.Tempest.tempestConfInit()

        caseResult = True;

        for ctrl in main.Cluster.runningNodes:
            try :
                if str(ctrl.ipAddress) == main.params[ 'Rally' ].get( 'ONOSRestIntfAddr' ) :
                    continue
            except Exception:
                pass
            main.step( "ONOS " + ctrl.name + " Down" )
            killResult = main.ONOSbench.onosDie( ctrl.ipAddress )
            main.log.info("onos Die " + ctrl.name)

            stepResult = main.Tempest.tempestTest("networkTest")
            if killResult != main.TRUE or stepResult != main.TRUE:
                caseResult = False;

            main.step( "ONOS " + ctrl.name + " ReStart" )
            startResult = main.ONOSbench.onosStart( ctrl.ipAddress )
            time.sleep(5)
            stepResult = main.Tempest.tempestTest("networkTest")
            if startResult != main.TRUE or stepResult != main.TRUE:
                caseResult = False;

        utilities.assert_equals( expect=True, actual=caseResult,
                                 onpass="Successfully ONOS Recovery test",
                                 onfail="Failed ONOS Recoverysssss test" )
