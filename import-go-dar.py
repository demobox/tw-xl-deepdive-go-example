import urllib, random
tempDarName = "%s_go.dar" % (random.randint(0, 1000000))
urllib.urlretrieve('https://xebia.egnyte.com/h-s-internal/20130821/f3a9341a763f49b9', tempDarName)
deployit.importPackage(tempDarName)