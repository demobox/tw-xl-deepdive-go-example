from java.util import List, ArrayList
from com.xebialabs.deployit.plugin.api.udm import ConfigurationItem
from com.xebialabs.deployit.engine.api.dto import ConfigurationItemId, Deployment, ValidatedConfigurationItem, Control
from com.xebialabs.deployit.plugin.api.reflect import DescriptorRegistry

###############
# ci.py
#
# This CLI extension module presents a more user-friendly interface to users of the CLI. Objects passing to and from the
# server are automatically wrapped and unwrapped in a Ci() instance. This Ci instance makes it possible to access regular
# properties and synthetic properties in the same way.
# Ci instances also contain methods for control tasks defined on the CI, if proxies are exposed.
#
# Example usage:
#
# Accessing CI synthetic values using dot-notation:
#
#	  env = factory.configurationItem('Environments/testEnv', 'udm.Environment')
#	  env.members = HashSet()
#	  # If 'owner' is a synthetic field defined on udm.Environment:
#	  env.owner = 'OPS'
#	  repository.create(env)
#
# Invoking control tasks:
#
#	  server = factory.configurationItem('Infrastructure/testServer', 'www.Webserver')
#	  # If 'start' is a control task (synthetic or otherwise) on www.Webserver:
#	  server.start()


###############
# Descriptor lookup map

###############
# Plumbing code to decorate, wrap & unwrap objects passing to and from the server

class CliObjectWrapperDecorator:
	delegate = None
	def __init__(self, delegate):
		self.delegate = delegate

	def __getattr__(self,name):
		return self.decorator(getattr(self.delegate,name))

	def decorator(self, target):
		def wrapper(*args):
			processedArgs = []
			for a in args:
				if isinstance(a, Ci):
					processedArgs.append(WrapperUnwrapper._unwrap(a))
				elif isinstance(a, List) or isinstance(a, type([])):
					processedArgs.append(WrapperUnwrapper._unwrapList(a))
				elif isinstance(a, DeploymentWrapper) or isinstance(a, ControlWrapper):
					processedArgs.append(a.unwrap())
				else:
					processedArgs.append(a)

			return WrapperUnwrapper._wrap(target(*processedArgs))

		return wrapper


# Class that wraps and unwraps objects retrieved from the Deployit server
class WrapperUnwrapper():
	# Wrap an object received from the server in a Ci if appropriate
	def _wrap(serverCi):
		if serverCi is None:
			return None
		if isinstance(serverCi,ConfigurationItem):
			return Ci(serverCi)
		if isinstance(serverCi,List):
			return WrapperUnwrapper._wrapList(serverCi)
		if isinstance(serverCi,Deployment):
			return DeploymentWrapper(serverCi.id, serverCi.deploymentType, Ci(serverCi.deployedApplication), WrapperUnwrapper._wrapList(serverCi.deployeds))
		if isinstance(serverCi,Control):
			return ControlWrapper(Ci(serverCi.configurationItem), serverCi.controlName, Ci(serverCi.parameters))
		return serverCi
	_wrap = staticmethod(_wrap)

	def _wrapList(cis):
		ciList = []
		for item in cis:
			if isinstance(item,unicode):
				ciList.append(str(item))
			elif isinstance(item, ConfigurationItem):
				ciList.append(Ci(item))
			else:
				ciList.append(item)
		return ciList
	_wrapList = staticmethod(_wrapList)

	# Unwrap a Ci instance so it can be passed back to the server
	def _unwrap(ci):
		if isinstance(ci, Ci):
			return ci._ci
		elif isinstance(ci, unicode):
			return str(ci)
		else:
			return ci
	_unwrap = staticmethod(_unwrap)

	def _unwrapList(cis):
		serverCiList = ArrayList()
		for item in cis:
			serverCiList.add(WrapperUnwrapper._unwrap(item))
		return serverCiList
	_unwrapList = staticmethod(_unwrapList)


###############
# Classes that wrap objects to/from the server and give them an easier to use interface

# Wrap CIs
class InterceptedMap():
	def __init__(self, ownerci):
		self.__dict__["_ci"] = ownerci

	def __setitem__(self, name, val):
		self._ci.setProperty(name, val)

	def __getitem__(self, name):
		return self._ci.getProperty(name)

class Ci():

	def __init__(self,delegate):
		self.__dict__["_ci"] = delegate

		# Create control task methods (if proxies exposed)
		try:
			descriptor = DescriptorRegistry.getDescriptor(delegate.type)
			controlTasks = descriptor.controlTasks
			for task in controlTasks:
				self.__dict__[task.name] = lambda: deployit.executeControlTask(task.name, self._ci)
		except:
			pass

	def __getitem__(self, name):
		return self._ci.getProperty(name)

	def __getattr__(self,name):
		if name == "_ci":
			return self.__dict__["_ci"]
		if name == "id":
			return self._ci.id
		elif name == "name":
			return self._ci.name
		elif name == "type":
			return str(self._ci.type)
		elif name == "values":
			return InterceptedMap(self._ci)
		elif name == "validations":
			if isinstance(self._ci, ValidatedConfigurationItem):
				return self._ci.validations
			else:
				return []
		return self._ci.getProperty(name)

	def __setattr__(self,name,val):
		if name == "id":
			self._ci.id = val
		elif name == "values":
			for k in val.keys():
				self._ci.setProperty(k, val[k])
		else:
			self._ci.setProperty(name, val)

	def __str__(self):
		return str(self._ci)

	def toString(self):
		return str(self._ci)

	def __repr__(self):
		return repr(self._ci)

	def __eq__(self, other):
		if isinstance(other, Ci):
			return self._ci == other._ci
		else:
			return false

	def describe(self):
		deployit.describe(str(self._ci.type))

	def prettyprint(self):
		deployit.print(self._ci)

	def create(self):
		return repository.create(self)

	def update(self):
		return repository.update(self)

	def delete(self):
		repository.delete(self.id)

	def _resolvePartialNameInListAttr(self,listPropertyName,partialName):
		found = None
		for member in self._ci.values[listPropertyName]:
			if member.endswith(partialName):
				if found is None:
					found = member;
				else:
					raise Exception("Partial name cannot be resolved because there is more that 1 potential match")
		return found

	def _searchByTypeAndParent(ciType,parent):
		return repository.search(ciType,parent)
	_searchByTypeAndParent = staticmethod(_searchByTypeAndParent)

	def _searchByType(ciType):
		return repository.search(ciType)
	_searchByType = staticmethod(_searchByType)



# Wrap the Deployment DTO object
class DeploymentWrapper():

	id = None
	deployedApplication = None
	deployeds = None
	deploymentType = None
	upgrade = False

	def __init__(self, id, deploymentType, deployedApplication, deployeds):
		self.deploymentType = deploymentType.toString()
		self.upgrade = (self.deploymentType == 'UPDATE');
		self.deployedApplication = deployedApplication
		self.deployeds = deployeds
		self.id = id

	def prettyprint(self):
		deployit.print(self.deployedApplication)
		for deployed in self.deployeds:
			deployit.print(deployed)

	def unwrap(self):
		serverDeployment = Deployment()
		serverDeployment.id = self.id
		serverDeployment.deploymentType = Deployment.DeploymentType.valueOf(self.deploymentType)
		if self.upgrade:
			serverDeployment.deploymentType = Deployment.DeploymentType.UPDATE
		serverDeployment.deployedApplication = WrapperUnwrapper._unwrap(self.deployedApplication)
		serverDeployment.deployeds = WrapperUnwrapper._unwrapList(self.deployeds)
		return serverDeployment

	def __str__(self):
		return str(self)

	def toString(self):
		return str(self)

	def __repr__(self):
		return "%s deployment of %s to %s." % (str(self.deploymentType).title(), str(self.deployedApplication.values['version']), str(self.deployedApplication.values['environment']))

class ControlWrapper():

	configurationItem = None
	controlName = None
	parameters = None

	def __init__(self, configurationItem, controlName, parameters):
		self.configurationItem = configurationItem
		self.controlName = controlName
		self.parameters = parameters

	def prettyprint(self):
		deployit.print(self.configurationItem)
		deployit.print(self.parameters)

	def unwrap(self):
		serverControl = Control(WrapperUnwrapper._unwrap(self.configurationItem), self.controlName, WrapperUnwrapper._unwrap(self.parameters))
		return serverControl

	def __str__(self):
		return str(self)

	def toString(self):
		return str(self)


###############
# Installation of the wrappers

factory = CliObjectWrapperDecorator(factory)
repository = CliObjectWrapperDecorator(repository)
deployit = CliObjectWrapperDecorator(deployit)
deployment = CliObjectWrapperDecorator(deployment)
security = CliObjectWrapperDecorator(security)
