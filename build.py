#coding:utf8
'''
首先生成nameMap.json
	通过读取所有.proto文件
	为每个protp文件分配一个id
	为文件中的每个message分配一个id
	保存为nameMap.json
'''

import os
import json
import re
import sys
import shutil
import tempfile

print sys.path
sys.path.append(".")

pat = re.compile('message (\w+)')

moduleID = 1

msgMap = {}
newMsgMap = {}

if os.path.exists('nameMap.json') :
	con = open('nameMap.json').read()
	msgMap = json.loads(con)
	
def getMsgID(moduleName):
	global msgMap
	msgID = 1
	for k in msgMap[moduleName] :   #遍历msgMap中的module的Message,给予大于最大的messageId的ID
		if k != 'id':
			if msgMap[moduleName][k] >= msgID:
				msgID = msgMap[moduleName][k] + 1
	return msgID
	
def getModuleID(modName):  #获取moduleID,返回的moduleID总是大于目前已经存在的ModuleID
	global moduleID
	global msgMap
	for k in msgMap:
		if msgMap[k]["id"] >= moduleID:
			moduleID = msgMap[k]["id"]+1
	if moduleID >= 256:
		raise Exception("Module Id too Big "+modName+" "+moduleID)
	return moduleID


#Begin here
f1 = os.listdir('protos')  #该文件夹下的所有的文件(包含dir和file)
allProtos = []

for i in f1:
	if i.find('.proto') != -1 and i.find('dump') == -1 and i.find('.swap') == -1:#找到只有.proto的文件(去除了dump和.swap等干扰)
		modName = i.replace('.proto', '')
		if msgMap.get(modName) == None and modName[0] == 'M':  #如果目录中的msgMap没有这个mod,并且proto的文件第一个字母为M,我们才关注写入nameMap
			msgMap[modName] = {"id":getModuleID(modName)}
			
		allProtos.append(i)
		profile = open("protos/" + i).read()  #读取这个proto文件
		
		mat = pat.findall(profile)
		for n in mat:
			if msgMap.get(modName) != None and msgMap[modName].get(n) == None: #如果读取的一个新的message没有在msgMap中
				if n[:2] == 'CG' or n[:2] == 'GC':  #我们只关心CG和GC的message
					print "Add Name is", n
					msgMap[modName][n] = getMsgID(modName)
			newMsgMap[n] = True  #这里记录了这个message
			
#检查是否有MsgName 在nameMap.json 里面但是不在 proto里 表示这个Message被删除了 可以从MsgName 中去掉
cleanMsgMap = {}

for mod in msgMap:  #实际上是遍历了一遍msgMap,把上面加入到newMsgMap中的message信息,从msgMap中提取出来放到了cleanMsgMap中,这个cleanMsgMap实际上存储的就是所有proto的message,而不再是nameMap.json中的信息  //其实可以一开始就删除nameMap.json,然后遍历重新生成
	newMod = {}
	for msg in msgMap[mod]:
		if msg != 'id':
			if newMsgMap.get(msg) != None:
				newMod[msg] = msgMap[mod][msg]
		else:
			newMod["id"] = msgMap[mod]["id"]
	cleanMsgMap[mod] = newMod

msgMap = cleanMsgMap

f = open('nameMap.json', 'w')
f.write(json.dumps(msgMap, indent=4, separators=(', ', ': ')))
f.close()


'''
	调用ProtoGen.exe把所有protos生成C#代码
'''
comStr = ''
for a in allProtos:
	comStr += 'protos/%s ' % (a)

print "all protos"

print "CMDIs"
fullCMD = 'mono ProtoGen.exe %s protos/google/protobuf/csharp_options.proto protos/google/protobuf/descriptor.proto --proto_path=protos' % (comStr)
print fullCMD
os.system(fullCMD)



'''
移动所有编辑出来的C#文件到cs文件夹中
'''
delFile = [
'Util2.cs',
'Util3.cs',
'CSharpOptions.cs',
'DescriptorProtoFile.cs',
]

if not os.path.exists("cs") :
	os.makedirs("cs")

f = os.listdir('.')
for i in f:
	if i.endswith(".cs"):
		if i in delFile:
			os.remove(i)
		else:
			shutil.move(i, "cs/%s" % (i))
			
'''
调用GenUtilFile.py把msgMap中的数据按照一定格式生成一个Util的c#类
'''
import GenUtilFile
GenUtilFile.GenUtil(msgMap.values())
f = os.listdir('.')



'''
移动py脚本,模板csproj和库文件
调用UpdateSln.py把C#文件放入new.csproj中
调用xbuild编译代码成dll
'''
shutil.copy2("UpdateSln.py", "cs/")
shutil.copy2("protoDll.csproj ", "cs/")
shutil.copy2("Google.ProtocolBuffersLite.dll", "cs/")
	
os.chdir('cs')
os.system('py.exe UpdateSln.py')
os.system('xbuild new.csproj')
os.chdir('..')