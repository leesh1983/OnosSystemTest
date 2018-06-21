#!/usr/bin/env python
"""
Created on 26-Oct-2012
Copyright 2012 Open Networking Foundation (ONF)

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

MininetCliDriver is the basic driver which will handle the Mininet functions

Some functions rely on a modified version of Mininet. These functions
should all be noted in the comments. To get this MN version run these commands
from within your Mininet folder:
    git remote add jhall11 https://github.com/jhall11/mininet.git
    git fetch jhall11
    git checkout -b dynamic_topo remotes/jhall11/dynamic_topo
    git pull


    Note that you may need to run 'sudo make develop' if your mnexec.c file
changed when switching branches."""
import pexpect
import sys
import os
from core.graph import Graph
from drivers.common.clidriver import CLI


class TempestCliDriver( CLI ):

    """
    tempest cli driver
    """
    def __init__( self ):
        super( TempestCliDriver, self ).__init__()
        self.handle = self
        self.name = None
        self.home = None
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0
        # TODO: Refactor driver to use these everywhere
        self.mnPrompt = "mininet>"
        self.hostPrompt = "\#"
        self.bashPrompt = "\$"
        self.myPrompt = '\#|\$'
        self.scapyPrompt = ">>>"
        self.graph = Graph()

    def connect( self, **connectargs ):
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = "~/"
            self.name = self.options[ 'name' ]
            for key in self.options:
                if key == "home":
                    self.home = self.options[ 'home' ]
                    break
            if self.home is None or self.home == "":
                self.home = "~/"

            try:
                if os.getenv( str( self.ip_address ) ) is not None:
                    self.ip_address = os.getenv( str( self.ip_address ) )
                else:
                    main.log.info( self.name +
                                   ": Trying to connect to " +
                                   self.ip_address )

            except KeyError:
                main.log.info( "Invalid host name," +
                               " connecting to local host instead" )
                self.ip_address = 'localhost'
            except Exception as inst:
                main.log.error( "Uncaught exception: " + str( inst ) )


            self.handle = super(
                TempestCliDriver,
                self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

            if self.handle:
                main.log.info( "Connection successful to the host " +
                               self.user_name +
                               "@" +
                               self.ip_address )
                return main.TRUE
            else:
                main.log.error( "Connection failed to the host " +
                                self.user_name +
                                "@" +
                                self.ip_address )
                main.log.error( "Failed to connect to the Mininet CLI" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disconnect( self ):
        response = main.TRUE
        try:
            if self.handle:
                self.handle.sendline( "" )
                self.handle.expect( self.myPrompt )
                self.handle.sendline( "exit" )
                self.handle.expect( "closed" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
        except ValueError:
            main.log.exception( "Exception in disconnect of " + self.name )
            response = main.TRUE
        except Exception:
            main.log.exception( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def tempestConfInit( self ):

        try:
            if self.handle:
                self.handle.sendline( "cd" )
                isBashPrompt = self.handle.expect( [self.bashPrompt, self.hostPrompt] )
                if isBashPrompt == 0 :
                    self.handle.sendline( ". rally/bin/activate" )
                    i = self.handle.expect( ["No such file or directory", self.myPrompt] )
                    if i == 0 :
                        main.log.error( "Failed Tempest Configuration." )
                        main.cleanAndExit()

                main.log.info( "Set Openrc" )
                cmd = main.params[ 'Rally' ].get( 'adminOpenrc' )
                self.handle.sendline( cmd )
                self.handle.expect( self.myPrompt )

                main.log.info( "Deployment Create" )
                cmd = main.params[ 'Rally' ].get( 'deploymentCreate' )
                self.handle.sendline( cmd )
                self.handle.expect( self.myPrompt )

                main.log.info( "Create verifier" )
                cmd = main.params[ 'Rally' ].get( 'createVerifier' )
                self.handle.sendline( cmd )
                self.handle.expect( self.myPrompt )

                main.log.info( "Configure verifier" )
                cmd = main.params[ 'Rally' ].get( 'configureVerifier' )
                self.handle.sendline( cmd )
                self.handle.expect( self.myPrompt )

                main.log.info( "Tempest Configuration successful." )
                return main.TRUE
            else:  # if no handle
                main.log.error( self.name + ": Connection failed to the host " +
                                self.user_name + "@" + self.ip_address )
                main.log.error( self.name + ": Failed to connect to TempestHost" )
                return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()

    def tempestBasicTest( self ):

        timeout=300
        try:
            if self.handle:
                self.handle.sendline( "cd" )
                isBashPrompt = False
                promptType = self.handle.expect( [self.bashPrompt, self.hostPrompt] )
                if promptType == 0 :
                    isBashPrompt = True

                promptIndex = -1
                cmd = main.params[ 'Rally' ].get( 'basicTest' )
                main.log.info( "Rally command: " + cmd +"\nPlease wait a moment.")
                self.handle.sendline( cmd )
                i = self.handle.expect( [ 'password\sfor\s',
                                          self.myPrompt,
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
                if i == 0:
                    # Sudo asking for password
                    main.log.info( self.name + ": Sending sudo password" )
                    self.handle.sendline( self.pwd )
                    i = self.handle.expect( [ '%s:' % self.user_name,
                                              self.prompt,
                                              pexpect.EOF,
                                              pexpect.TIMEOUT ],
                                            timeout )

                resultFullStr = str( self.handle.before )
                if i == 1:
                    index = resultFullStr.rfind("Totals\r\n======")
                    if isBashPrompt:
                        promptIndex = resultFullStr.rfind("(rally)")
                    else:
                        promptIndex = resultFullStr.rfind(self.user_name + "@")
                    if index != -1 :
                        if promptIndex != -1 :
                            resultStr = resultFullStr[index+14:promptIndex]
                        else :
                            resultStr = resultFullStr[index+14:]
                        main.log.info( "Basic test result\n" + resultStr)

                    if 'Failures: 0' in resultStr :
                        return main.TRUE

                main.log.error( "Basic test failed (expect index:" + str(i) +")" )
                if promptIndex != -1:
                    main.log.warn( resultFullStr[:promptIndex] )
                else :
                    main.log.warn( resultFullStr )
                return main.FALSE
            else:  # if no handle
                main.log.error( self.name + ": Connection failed to the host " +
                                self.user_name + "@" + self.ip_address )
                main.log.error( self.name + ": Failed to connect to TempestHost" )
                return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()

