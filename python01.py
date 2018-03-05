import re
import os
from transliterate import translit

# -*- coding: utf-8 -*-
interf = input('Введите интерфейс \n')
uni = input('Введите №.юнита \n')
svlan = input('Введите Svlan \n')
cvlan = input('Введите inner-vlan \n')
cpe = input('Введите hostname CPE \n')
cpeport = input('Введите порт на CPE \n')
#family = input('Введите ФИО \n')
pp = input('Введите №ПП \n')
bw = input('Название скоростного полисера на терминации "limXm" \n')
date = (os.popen("date +%d.%m.%Y").read()).strip()
#comandcpip = print('ping' + ' ' +  cpe + '-c 1 | grep PING | awk \'{print $3}\'')
#cpeip = os.popen("ping " + cpe " -c 1 | grep PING | awk '{print $3}'").read()
DATE = str(date) 

resultlist = []
vardict = {}

# тут придумать что делать с полиесром resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni 'family inet filter input' PochtaRF-512k-50-25-25-in





with open('temp01', 'r') as f:
    fiz = re.compile('Примечание: Адрес предоставления услуги:\s(?P<x>.*)', re.M)
    fizaddr = fiz.findall(f.read()) 
    if fizaddr:
        fizaddr = translit(','.join(fizaddr), 'ru', reversed=True)
        vardict['fizaddr'] = str(fizaddr)
with open('temp01', 'r') as f:
    for line in f:
        ipmask = re.search('([0-9]+\.)+[0-9]+\s(\/\d{2})', line) 
        ipad = re.search('(([0-9]+\.)+[0-9]+)\s+Адрес\sРОСТЕЛЕКОМ', line)
        cms = re.search('(CMS\S)\s*(\d+\S\d+\S\d?)', line)
        surms = re.search('Дата и номер:\s*(\d+\.)+\d+\s\S(\d+)', line)
        vpn = re.search('^VPN ID:\s(\d*)', line)
        clientname = re.search('^Тема:\s(.*)', line) 
        if ipmask:
             ipmask = ipmask.group(2)
             vardict['ipmask'] = str(ipmask)
        elif ipad:
             ipad = ipad.group(1)
             vardict['ipad'] = str(ipad)
        elif cms:
             cms = cms.group(1) + cms.group(2)
             vardict['cms'] = str(cms) 
        elif surms:
             surms = surms.group(2)
             vardict['surms'] = str(surms)
        elif vpn:
             vpn = vpn.group(1)
             vardict['vpn'] = str(vpn)
        elif clientname:
             clientname = translit(clientname.group(1), reversed=True)
             vardict['clientname'] = str((clientname.lower()).capitalize())
        else:
             continue 
#print(vardict.get('fizaddr'))
#print(vardict)
print('-'*100)
if vardict.get('vpn'):
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'description \"##VPN:v' + vardict.get('vpn') + ',' + ' ' + vardict.get('clientname') + ', ' + 'SURMS:' + vardict.get('surms')+ ',' + ' ' + DATE + ' ' + '|' + ' ' + 'SVL:' + svlan + ' ' + 'CVL:' + cvlan + ',' + ' ' + vardict.get('fizaddr') + ' ' + '|' + ' ' + cpe + ':' + cpeport + ' ' +  '|' + ' ' + 'pp' + pp + ' ' + '|' + ' ' + 'Motovilov' +' ' + '##\"')
else:
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'description \"##INET,' + ' ' + vardict.get('clientname') + ', ' + 'SURMS:' + vardict.get('surms')+ ',' + ' ' + DATE + ' ' + '|' + ' ' + 'SVL:' + svlan + ' ' + 'CVL:' + cvlan + ',' + ' ' + vardict.get('fizaddr') + ' ' + '|' + ' ' + cpe + ':' + cpeport + ' ' + '|' + ' ' + 'pp' + pp + ' ' + '|' + ' ' + 'Motovilov' +' ' + '##\"')
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'vlan-tags outer' + ' ' + svlan)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'vlan-tags inner' + ' ' + cvlan)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet rpf-check')
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet policer input ' +  bw)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet policer output ' +  bw)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet address' + ' ' + vardict.get('ipad') + vardict.get('ipmask'))
if vardict.get('vpn'):
    resultlist.append('set routing-instances' + ' ' + 'v' + vardict.get('vpn') + '####Здесь допиши имя инстанса!!!####' + ' ' + 'interface' + ' ' + interf + '.' + uni  ) 
else:
    pass 
print('\n'.join(resultlist))       

