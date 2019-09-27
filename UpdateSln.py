#coding:utf8
import os
import re

pat = re.compile('Compile Include')

res = ''
template = '    <Compile Include="%s" />\n'
replace = '' 
allFiles = os.listdir('.')
for f in allFiles:
    if f.find('.cs') != -1 and f.find('.cspr') == -1:
        replace += template % (f)



f = open('protoDll.csproj').readlines()
first = True
for l in f:
    if len(pat.findall(l)) > 0:
        if first:
            res += replace
            first = False
        else:
            pass
    else:
        res += l

nf = open('new.csproj', 'w')
nf.write(res)
nf.close()
