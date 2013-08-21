@echo off
REM
REM Batch script to start the Deployit CLI
REM

setlocal ENABLEDELAYEDEXPANSION

REM Get Java executable
if "%JAVA_HOME%"=="" (
  set JAVACMD=java
) else (
  set JAVACMD="%JAVA_HOME%\bin\java"
)

REM Get JVM options
if "%DEPLOYIT_CLI_OPTS%"=="" (
  set DEPLOYIT_CLI_OPTS=-Xmx512m -XX:MaxPermSize=256m
)

REM Get Deployit cli home dir
if "%DEPLOYIT_CLI_HOME%"=="" (
  cd /d "%~dp0"
  cd ..
  set DEPLOYIT_CLI_HOME=!CD!
)

cd /d "%DEPLOYIT_CLI_HOME%"

REM Build Deployit cli classpath
set DEPLOYIT_CLI_CLASSPATH=conf
for %%i in (hotfix\*.jar) do set DEPLOYIT_CLI_CLASSPATH=!DEPLOYIT_CLI_CLASSPATH!;%%i
for %%i in (lib\*.jar) do set DEPLOYIT_CLI_CLASSPATH=!DEPLOYIT_CLI_CLASSPATH!;%%i
for %%i in (plugins\*.jar) do set DEPLOYIT_CLI_CLASSPATH=!DEPLOYIT_CLI_CLASSPATH!;%%i

REM Run Deployit cli
%JAVACMD% %DEPLOYIT_CLI_OPTS% -classpath "%DEPLOYIT_CLI_CLASSPATH%" com.xebialabs.deployit.cli.Cli %*

:end
endlocal

