
class HAsonaClustering:

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
        main.ONOSbench.setOnosNetCfg(hostIp=main.Cluster.next().ipAddress, cfgFile=main.params[ 'networkCfg' ].get( 'path' ))

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

    def CASE2( self, main ):
        """
            Tempest basic Test
        """
        main.case( "Tempest basic test" )
        main.step( "Tempest configure" )
        main.Tempest.tempestConfInit()

        main.step( "Basic test" )
        stepResult = main.Tempest.tempestTest("basicTest")
        utilities.assert_equals( expect=main.TRUE, actual=stepResult,
                                 onpass="Successfully basic test",
                                 onfail="Failed basic test" )

    def CASE3( self, main):
        """
            ONOS Failure Test
        """
        main.case( "ONOS Failure test" )

        main.step( "Tempest configure" )
        main.Tempest.tempestConfInit()

        caseResult = True;
        main.step( "ONOS Down test" )
        for ctrl in main.Cluster.runningNodes:
            try :
                if str(ctrl.ipAddress) == main.params[ 'Rally' ].get( 'ONOSRestIntfAddr' ) :
                    continue
            except Exception:
                pass

            killResult = main.ONOSbench.onosDie( ctrl.ipAddress )
            main.log.info("onos Die " + ctrl.name)

            stepResult = main.Tempest.tempestTest("networkTest")
            if killResult != main.TRUE or stepResult != main.TRUE:
                caseResult = False;

        main.step( "ONOS ReStart test" )
        for ctrl in main.Cluster.runningNodes:
            startResult = main.ONOSbench.onosStart( ctrl.ipAddress )
            stepResult = main.Tempest.tempestTest("networkTest")
            if startResult != main.TRUE or stepResult != main.TRUE:
                caseResult = False;

        utilities.assert_equals( expect=True, actual=caseResult,
                                 onpass="Successfully ONOS Failure test",
                                 onfail="Failed ONOS Failure test" )



    def CASE4( self, main):
        """
            SONA Application Failure Test
        """
        main.case( "SONA App Failure test" )

        main.step( "Tempest configure" )
        main.Tempest.tempestConfInit()

        caseResult = True;
        main.step( "SONA App Down test" )
        for ctrl in main.Cluster.runningNodes:
            downResult = ctrl.CLI.app( "org.onosproject.openstacknetworking", "deactivate" )
            stepResult = main.Tempest.tempestTest("networkTest")
            if downResult != main.TRUE or stepResult != main.TRUE:
                caseResult = False;
            upResult = ctrl.CLI.app( "org.onosproject.openstacknetworking", "activate" )
            stepResult = main.Tempest.tempestTest("networkTest")
            if upResult != main.TRUE or stepResult != main.TRUE:
                caseResult = False;

        utilities.assert_equals( expect=True, actual=caseResult,
                                 onpass="Successfully SONA App Failure test",
                                 onfail="Failed SONA App Failure test" )

