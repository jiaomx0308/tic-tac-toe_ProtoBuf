#coding:utf8
#生成每个Message 对应的GetMsg 的代码
UtilTemplate = '''
using UnityEngine;
using System.Collections.Generic;
using Google.ProtocolBuffers;


namespace MyLib {
public partial class Util {
	public delegate IMessageLite MsgDelegate(ByteString buf); 
	
%s

	static Dictionary<string, MsgDelegate> msgMap = new Dictionary<string, MsgDelegate>(){
%s
	};

	public static IMessageLite GetMsg(int moduleId, int messageId, ByteString buf) {
		//var module = SaveGame.saveGame.getModuleName(moduleId);
		var msg = SaveGame.saveGame.getMethodName(moduleId, messageId);
		Debug.LogWarning ("modulename "+moduleId+" "+messageId+" msg "+msg);

		return msgMap[msg](buf);
	}
}

}
'''

delegateTemplate = '''
	static IMessageLite Get%s(ByteString buf) {
		var retMsg = MyLib.%s.ParseFrom(buf);
		return retMsg;
	}	
'''
initTemplate = '''
	{"%s", Get%s},
'''

'''
msgList = [msgName, msgName]
'''
def GenUtil(msgList):
	funcList = ''
	initList = ''
	for m in msgList:
		#print 'gen module', m
		for s in m:
			if s != 'id':
				funcList += delegateTemplate % (s, s)
				initList += initTemplate % (s, s)

	#print funcList
	#print initList
	ret = UtilTemplate % (funcList.encode('utf8'), initList.encode('utf8')) 
	print 'write Util2.cs '
	temp = chr(0xef)+chr(0xbb)+chr(0xbf)+ret
	f = open('Util2.cs', 'w')
	
	f.write(temp)
	f.close()