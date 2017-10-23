import re

# -*- coding: utf-8 -*-
interf = input('Введите интерфейс \n')
uni = input('Введите №.юнита \n')
svlan = input('Введите Svlan \n')
cvlan = input('Введите inner-vlan \n')
pp = input('Введите №ПП')
bw = input('Название скоростного полисера на терминации "limXm"')



resultlist = []
vardict = {}

resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet rpf-check')
# тут придумать что делать с полиесром resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni 'family inet filter input' PochtaRF-512k-50-25-25-in
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet policer arp per-int-arp-policer')






with open('temp01', 'r') as f:
    for line in f:
        ipmask = re.search('([0-9]+\.)+[0-9]+\s(\/\d{2})', line) 
        ipad = re.search('(([0-9]+\.)+[0-9]+)\s+Адрес\sРОСТЕЛЕКОМ', line)
        cms = re.search('(CMS\S)\s*(\d+\S\d+\S\d?)', line)
        surms = re.search('Дата и номер:\s*(\d+\.)+\d+\s\S(\d+)', line)
        vpn = re.search('\S+\sVPN:\s(\S+)\s\(\S+\)', line)
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
        else:
             continue 
#print(vardict)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'description \"##XXX SURMS:' + vardict.get('surms') + ' ' + vardict.get('cms') + ' '+ 'pp' + pp + ' ' + '##\"')
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'vlan-tags outer' + ' ' + svlan)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'vlan-tags inner' + ' ' + cvlan)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet rpf-check')
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet policer input lim' + vardict.get('speed') + bw)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet policer output lim' + vardict.get('speed') + bw)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet address' + ' ' + vardict.get('ipad') + vardict.get('ipmask'))
if vardict.get('vpn'):
    resultlist.append('set routing-instances' + ' ' + vardict.get('vpn') + ' ' + 'interface' + ' ' + interf + '.' + uni) 
else:
    pass 
print('\n'.join(resultlist))        
