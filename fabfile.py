from fabric.api import *
from fabric.tasks import execute
import nova, time

env.user = 'core'
env.key_filename = '/home/vcd/code/websync/TreasureKey.pem'
#env.hosts = ['core@130.240.233.101']

def makeInstance():
	instance = nova.spawnInstance()
	if instance:
		serverIP = nova.assignFloatingIP(instance)
		env.hosts = [serverIP]
		print(serverIP)
	time.sleep(5)

#def removeInstance():
#todo

def setupDocker():
	print(env.hosts)
	run('uname -a')

if __name__ == '__main__':
	makeInstance()
	execute(setupDocker)

