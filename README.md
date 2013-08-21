# Finishing up the Deployit Deepdive

## Setting up the Deployit server

```
unzip /path/to/deployit-server-zip.zip -d /deployit/server/dir
cd /deployit/server/dir
git init
git remote add config https://github.com/demobox/tw-xl-deepdive-config
git fetch config
git checkout master
cp available-plugins/*.jar plugins # do not overwrite existing files if prompted
bin/server.sh -setup -reinitialize # answer 'yes' when prompted
bin/server.sh &

# now import the repository contents and Go DAR
cd /some/other/dir
git clone https://github.com/demobox/tw-xl-deepdive-go-example
cd tw-xl-deepdive-go-example/deployit-3.9.3-069fc79-cli
bin/cli.sh -username admin -password admin -q -f ../repository-export.py # produced by the [export script](https://raw.github.com/xebialabs/community-plugins/master/cli-scripts/repository-export/export.py)
bin/cli.sh -username admin -password admin -q -f ../import-go-dar.py
```

Change the `workingDirectory` value for `Configuration/Templates/Hosts/vagrant-simple-server` and `Configuration/Templates/Hosts/vagrant-simple` to match your Vagrant setup.

## Creating the Go environment

Pretty much what we did. I added some logic to automatically tag **one** of the images as the Go server image:
```
<tags>
  <#if hostTemplate.name?ends_with("server")><value>go-server</value></#if>
  <value>go-agent</value>
</tags>
```
We also now have access to the `${sequenceNumber}` variable in all commands, and the `${params}` variable in the "create" and "find IP address" commands:
```
findIpAddressCommand: vagrant ssh ${hostTemplate.templateName}${sequenceNumber} -c ifconfig
```

## New deployed types

I cleaned up the low-level usage of `cmd2.Command` and `cmd2.CommandFolder` and created a couple of new types (in SERVER_HOME/ext/synthetic.xml):
```
<type type="apt.InstalledPackage" extends="generic.ExecutedScript" container-type="overthere.SshHost" deployable-type="apt.PackageSpec">
  <generate-deployable type="apt.PackageSpec" extends="generic.Resource" />
  <property name="packageName" />
  <property name="updateRepository" kind="boolean" required="false" />
  ...
</type>

<type type="go.DeployedAgent" extends="generic.ExecutedScriptWithDerivedArtifact" container-type="overthere.SshHost" deployable-type="go.Agent">
  <generate-deployable type="go.Agent" extends="generic.Folder" />
  <property name="targetDirectory" />
  <property name="server" kind="ci" referenced-type="go.DeployedServer" />
  <!-- admin properties -->
  ...
  <!-- we want this to come after smoke tests for the server -->
  <property name="createOrder" kind="integer" hidden="true" default="130" />
  ...
</type>

<type type="go.DeployedServer" extends="generic.ExecutedScriptWithDerivedArtifact" container-type="overthere.SshHost" deployable-type="go.Server">
  <generate-deployable type="go.Server" extends="generic.Folder" />
  <property name="targetDirectory" />
  <property name="port" kind="integer" default="8153" />
  ...
</type>
```

As an example, `install-go-agent.sh.ftl` looks like this:
```
#!/bin/sh -e
DAEMON=Y
export DAEMON
JAVA_HOME=${deployed.container.javaHome}
export JAVA_HOME
GO_SERVER=${deployed.server.container.address}
export GO_SERVER
GO_SERVER_PORT=${deployed.server.port}
export GO_SERVER_PORT
 
rm -rf ${deployed.targetDirectory}
mkdir -p ${deployed.targetDirectory}
mv go-agent-*/go-agent-*/* ${deployed.targetDirectory}
chown -R $USER:$USER ${deployed.targetDirectory}
echo Starting Go agent
chmod +x ${deployed.targetDirectory}/*.sh
${deployed.targetDirectory}/agent.sh
sleep 2
```

## Deploying Go

Combining the Go deployment package and newly-provisioned environment in the workspace and using the "auto-map all" double-arrow should result in the following:

![Result after auto-map all](http://i.imgur.com/exvehIc)

For the first deployment of the two agents, we need to select the Go server that we will reference:

![Choosing a Go server for an agent](http://i.imgur.com/IVVuDYp)

As discussed, this is not strictly necessary and could be avoided - it's mainly intended as an example of including references to other items in the deployment model.

![Deployment plan complete](http://i.imgur.com/AgZ2gBu.png)

![Go agent page](http://i.imgur.com/yekWo5Q)