from java.util import ArrayList

def create(id, type, values):
   return factory.configurationItem(id, type, values)

def verifyNoValidationErrors(entity):
   print "Validaing ci of type:", entity.type
   if entity.validations is None or len(entity.validations) == 0:
       return entity
   else:
       raise Exception("Validation errors are present! " + entity.validations.toString())

def verifyNoValidationErrorsInRepoObjectsEntity(repositoryObjects):
   for repoObject in repositoryObjects:
       verifyNoValidationErrors(repoObject)

def saveRepositoryObjectsEntity(repoObjects):
	print "Saving repository objects"
	repositoryObjects = repository.create(repoObjects)
	verifyNoValidationErrorsInRepoObjectsEntity(repositoryObjects)
	print "Saved repository objects"
	return repositoryObjects

def save(listOfCis):
	return saveRepositoryObjectsEntity(listOfCis)




infrastructureList = []

infrastructureList.append(create('Infrastructure/vagrantHost','overthere.LocalHost',{'tags':[],'os':'WINDOWS','deploymentGroup':'0'}))
infrastructureList.append(create('Infrastructure/vagrantHost/deployit-server-test-runner','tests2.TestRunner',{'tags':[],'host':'Infrastructure/vagrantHost','envVars':{},'deploymentGroup':'0'}))
save(infrastructureList)


environmentsList = []
save(environmentsList)


configurationList = []

configurationList.append(create('Configuration/Templates','core.Directory',{}))
configurationList.append(create('Configuration/Templates/Hosts','core.Directory',{}))
configurationList.append(create('Configuration/Templates/Hosts/vagrant-simple','vagrant.HostTemplate',{'findIpAddressRegex':'eth1.*?\\s*inet addr:(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})\\s+','xmlDescriptor':'<#escape x as x?xml>\n  <list>\n    <vagrant.SshHost id="${hostsPath}/${hostTemplate.templateName}_${hostAddress}">\n      <template ref="${hostTemplate.id}"/>\n      <vagrantHost ref="Infrastructure/vagrantHost" />\n      <cloudId>${cloudId}</cloudId>\n      <address>${hostAddress}</address>\n      <#if hostTemplate.privateKeyFile??><privateKeyFile>${hostTemplate.privateKeyFile}</privateKeyFile></#if>\n      <javaHome>/usr</javaHome>\n      <tags>\n        <#if hostTemplate.name?ends_with("server")><value>go-server</value></#if>\n        <value>go-agent</value>\n      </tags>\n    </vagrant.SshHost>\n  </list>\n</#escape>','retryDelay':'5','bootTimeout':'500','findIpAddressCommand':'vagrant ssh ${hostTemplate.templateName}${sequenceNumber} -c ifconfig','templateName':'simple','workingDirectory':'/path/to/your/vagrant/dir'}))
configurationList.append(create('Configuration/Templates/Hosts/vagrant-simple-server','vagrant.HostTemplate',{'findIpAddressRegex':'eth1.*?\\s*inet addr:(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})\\s+','xmlDescriptor':'<#escape x as x?xml>\n  <list>\n    <vagrant.SshHost id="${hostsPath}/${hostTemplate.templateName}_${hostAddress}">\n      <template ref="${hostTemplate.id}"/>\n      <vagrantHost ref="Infrastructure/vagrantHost" />\n      <cloudId>${cloudId}</cloudId>\n      <address>${hostAddress}</address>\n      <#if hostTemplate.privateKeyFile??><privateKeyFile>${hostTemplate.privateKeyFile}</privateKeyFile></#if>\n      <javaHome>/usr</javaHome>\n      <tags>\n        <#if hostTemplate.name?ends_with("server")><value>go-server</value></#if>\n        <value>go-agent</value>\n      </tags>\n    </vagrant.SshHost>\n  </list>\n</#escape>','retryDelay':'5','bootTimeout':'500','findIpAddressCommand':'vagrant ssh ${hostTemplate.templateName}${sequenceNumber} -c ifconfig','templateName':'simple','workingDirectory':'/path/to/your/vagrant/dir'}))
configurationList.append(create('Configuration/Templates/small-go-env','byoc.EnvironmentTemplate',{'xmlDescriptor':'<#escape x as x?xml>\n  <list>\n    <cloud.Environment id="${environmentId}">\n      <members>\n        <#list hosts as h>\n          <ci ref="${h.id}" />\n          <#list h.tags as tag>\n            <#if tag == "go-server">\n              <#assign goServerAddress=h.address />\n            </#if>\n          </#list>\n        </#list>\n        <ci ref="Infrastructure/vagrantHost/deployit-server-test-runner" />\n      </members>\n      <dictionaries>\n        <ci ref="${environmentId}_Settings" />\n      </dictionaries>\n    </cloud.Environment>\n    <udm.Dictionary id="${environmentId}_Settings">\n      <entries>\n        <#if goServerAddress??><entry key="GO_SERVER">${goServerAddress}</entry></#if>\n        <entry key="GO_SERVER_PORT">8153</entry>\n        <entry key="GO_SERVER_TARGET_DIRECTORY">/opt/go-server</entry>\n        <entry key="GO_AGENT_TARGET_DIRECTORY">/opt/go-agent</entry>\n      </entries>\n    </udm.Dictionary>\n  </list>\n</#escape>','description':'An environment with one host for a Go server and local agent','hostTemplates':['Configuration/Templates/Hosts/vagrant-simple','Configuration/Templates/Hosts/vagrant-simple-server']}))
save(configurationList)