#!/bin/sh
#
# Shell script to start the Deployit CLI
#

# Get Java executable
if [ -z "$JAVA_HOME" ] ; then
  JAVACMD=java
else
  JAVACMD="${JAVA_HOME}/bin/java"
fi

# Get JVM options
if [ -z "$DEPLOYIT_CLI_OPTS" ] ; then
  DEPLOYIT_CLI_OPTS="-Xmx512m -XX:MaxPermSize=256m"
fi

# Get Deployit cli home dir
if [ -z "$DEPLOYIT_CLI_HOME" ] ; then
  BIN_DIR=`dirname "$0"`
  cd "$BIN_DIR"
  ABSOLUTE_BIN_DIR=`pwd`
  DEPLOYIT_CLI_HOME=`dirname "$ABSOLUTE_BIN_DIR"`
elif [ ! -d "$DEPLOYIT_CLI_HOME" ] ; then
  echo "Directory $DEPLOYIT_CLI_HOME does not exist"
  exit 1
fi

cd "$DEPLOYIT_CLI_HOME"

# Build Deployit cli classpath
DEPLOYIT_CLI_CLASSPATH='conf'
for each in `ls hotfix/*.jar lib/*.jar plugins/*.jar 2>/dev/null`
do
  if [ -f $each ]; then
    DEPLOYIT_CLI_CLASSPATH=${DEPLOYIT_CLI_CLASSPATH}:${each}
  fi
done

# Run Deployit cli
$JAVACMD $DEPLOYIT_CLI_OPTS -classpath "${DEPLOYIT_CLI_CLASSPATH}" com.xebialabs.deployit.cli.Cli "$@"
