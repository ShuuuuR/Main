import re
import os
import paramiko
import getpass
import time
from transliterate import translit

# -*- coding: utf-8 -*-
interf = input('Введите интерфейс \n')
#uni = input('Введите №.юнита \n')
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
#cpeip = str((os.popen("ping -c 1 " + cpe )).readlines(-1)[0].split()[2])
DATE = str(date) 

def short_names(name):
    table = (
        ("Pochta rossii fgup", "Pochta RF"),
        ("Fgbu iats sudebnogo departamenta", "Upravlenie sudebnogo departamenta"),
        ("Fgup rchts tsfo ", "FGUP RchZ"),
        (" Habarovskij kraj,", ""),
        ("Evrejskaja avtonomnaja oblast'", "EAO"),
        ("Habarovskij kraj,", ""),
        (" Habarovskij kraj.,", ""),
        (" Habarovskij r-n.,", ""),
        (" Komsomol'sk-na-Amure", "KMS"),
        ("s. ", ""),
        ("ul. ", ""),
        (" d.", ""),
        ("dom. ", ""),
        ("prospekt", "pr-t"),
        (" ,", ","),
        ("'", ""),
        ("ja", "ya"),
        ("Ja", "Ya"),
    )
    for s_in, s_out in table:
        name = name.replace(s_in, s_out)
    return name


resultlist = []
vardict = {}

# тут придумать что делать с полиесром resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni 'family inet filter input' PochtaRF-512k-50-25-25-in





with open('temp01', 'r') as f:
    fiz = re.compile('Примечание: Адрес предоставления услуги:\s(?P<x>.*)', re.M)
    fizaddr = fiz.findall(f.read()) 
    if fizaddr:
        fizaddr = translit(','.join(fizaddr), 'ru', reversed=True)
        vardict['fizaddr'] = str(short_names(fizaddr))
with open('temp01', 'r') as f:
    for line in f:
        ipmask = re.search('([0-9]+\.)+[0-9]+\s(\/\d{2})', line) 
        ipad = re.search('(([0-9]+\.)+[0-9]+)\s+Адрес\sРОСТЕЛЕКОМ', line)
        cms = re.search('(CMS\S)\s*(\d+\S\d+\S\d?)', line)
        surms = re.search('Дата и номер:\s*(\d+\.)+\d+\s\S(\d+)', line)
        vpn = re.search('^VPN ID:\s(\d*)', line)
        clientname = re.search('^Тема:\s(.*)', line) 
        l2vpn = re.search('^.*включить клиента в L2 VPN.*', line)
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
             vpn = 'v' + vpn.group(1)
             vpn = str(vpn)
             command_0 = 'show configuration routing-instances | match ' + vpn + ' | display set | match instance-type'
             command_1 = 'show configuration interfaces ' + interf + ' | match "unit " | no-more' + '\n'
             #USER_S14 = input('Username_for_S14: ')
             USER_S14 = 'USER'
             #PASSWORD_S14 = getpass.getpass(prompt='Password_for_S14:')
             PASSWORD_S14 = 'PASS'
             S14_IP = '###IPADDR_S14####'
             sshS14 = paramiko.SSHClient()
             sshS14.set_missing_host_key_policy(paramiko.AutoAddPolicy())
             sshS14.connect(hostname=S14_IP, username=USER_S14, password=PASSWORD_S14, look_for_keys=False, allow_agent=False)
             with sshS14.invoke_shell() as ssh:
                 #USER_BPE1 = input('Username_for_BPE1: ')
                 USER_BPE1 = 'USER'
                 #PASSWORD_BPE1 = getpass.getpass(prompt='Password_for_BPE1:')
                 PASSWORD_BPE1 = 'PASS'
                 ssh.send('telnet <####IPADDR_BPE1####>\n')
                 time.sleep(1)
                 ssh.send(USER_BPE1 +'\n')
                 time.sleep(1)
                 ssh.send(PASSWORD_BPE1 + '\n')
                 time.sleep(3)
                 ssh.recv(1000)
                 ssh.send(command_1 + '\n')
                 time.sleep(3)
                 result1 = ssh.recv(5000).decode('utf-8')
                 ssh.send(command_0 + '\n')
                 time.sleep(3)
                 result0 = ssh.recv(5000).decode('utf-8')
                 #получил нужное значение регекспом, но нужно придумать как сделать так, чтобы вывод парамико уже был в одну строку.
                 unit_num_list = re.findall('unit (\d+) {', result1)
                 vpn_name = re.search('.*set routing-instances (v\d{4}-\S+)\s.*', result0)
                 #Задаем для них переменные
                 vpn_full_name = vpn_name.group(1)
                 vardict['vpn_full_name'] = str(vpn_full_name)
                 #Получаем список свободных юнитов:
                 free_unit_list =[] #создаем пустой список
                 #и дальше добавляем в него свободные значения:
                 for line in range(16384):
                     if str(line) not in unit_num_list:
                         free_unit_list.append(str(line))
                 uni = free_unit_list[4]
        elif clientname:
             #print(clientname.group(1))
             clientname = translit(clientname.group(1), reversed=True)
             vardict['clientname'] = str(short_names((clientname.lower()).capitalize()))
        elif l2vpn:
             vardict['l2vpn'] = str(l2vpn.group())
        else:
             continue 
print('-'*100)
if vardict.get('l2vpn'):
    command_1 = 'show configuration interfaces ' + interf + ' | match "unit " | no-more' + '\n'
    #USER_S14 = input('Username_for_S14: ')
    USER_S14 = 'USER'
    #PASSWORD_S14 = getpass.getpass(prompt='Password_for_S14:')
    PASSWORD_S14 = 'PASS'
    S14_IP = '###IPADDR_S14####'
    sshS14 = paramiko.SSHClient()
    sshS14.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshS14.connect(hostname=S14_IP, username=USER_S14, password=PASSWORD_S14, look_for_keys=False, allow_agent=False)
    with sshS14.invoke_shell() as ssh:
        #USER_BPE1 = input('Username_for_BPE1: ')
        USER_BPE1 = 'USER'
        #PASSWORD_BPE1 = getpass.getpass(prompt='Password_for_BPE1:')
        PASSWORD_BPE1 = 'PASS'
        ssh.send('telnet <####IPADDR_BPE1####>\n')
        time.sleep(1)
        ssh.send(USER_BPE1 +'\n')
        time.sleep(1)
        ssh.send(PASSWORD_BPE1 + '\n')
        time.sleep(3)
        ssh.recv(1000)
        ssh.send(command_1 + '\n')
        time.sleep(3)
        result1 = ssh.recv(5000).decode('utf-8')
        unit_num_list = re.findall('unit (\d+) {', result1)
        free_unit_list =[] #создаем пустой список
        for line in range(16384):
            if str(line) not in unit_num_list:
                free_unit_list.append(str(line))
        uni = free_unit_list[4]
    resultlist.append('set interfaces' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'description \"##L2VPN,' + ' ' + vardict.get('clientname') + ',' + 'SURMS:' + vardict.get('surms')+ ',' + ' ' + DATE + ' ' + '|' + ' ' + 'SVL:' + svlan + ' ' + 'CVL:' + cvlan + ',' + ' ' + vardict.get('fizaddr') + ' ' + '|' + ' ' + cpe + ':' + cpeport + ' ' +  '|' + ' ' + 'pp' + pp + ' ' + '|' + ' ' + 'Motovilov' +' ' + '##\"') 
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'apply-groups-except arp-police')
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'encapsulation vlan-ccc')
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'input-vlan-map pop-pop')
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'input-vlan-map push-push')


elif vardict.get('vpn_full_name'):
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'description \"##VPN:' + vardict.get('vpn_full_name') + ',' + ' ' + vardict.get('clientname') + ', ' + 'SURMS:' + vardict.get('surms')+ ',' + ' ' + DATE + ' ' + '|' + ' ' + 'SVL:' + svlan + ' ' + 'CVL:' + cvlan + ',' + ' ' + vardict.get('fizaddr') + ' ' + '|' + ' ' + cpe + ':' + cpeport + ' ' +  '|' + ' ' + 'pp' + pp + ' ' + '|' + ' ' + 'Motovilov' +' ' + '##\"')
    resultlist.append('set routing-instances' + ' ' + vardict.get('vpn_full_name') + ' ' + 'interface' + ' ' + interf + '.' + uni  )
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet rpf-check')
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet address' + ' ' + vardict.get('ipad') + vardict.get('ipmask'))
else:
    command_1 = 'show configuration interfaces ' + interf + ' | match "unit " | no-more' + '\n'
    #USER_S14 = input('Username_for_S14: ')
    USER_S14 = 'USER'
    #PASSWORD_S14 = getpass.getpass(prompt='Password_for_S14:')
    PASSWORD_S14 = 'PASS'
    S14_IP = '###IPADDR_S14####'
    sshS14 = paramiko.SSHClient()
    sshS14.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshS14.connect(hostname=S14_IP, username=USER_S14, password=PASSWORD_S14, look_for_keys=False, allow_agent=False)
    with sshS14.invoke_shell() as ssh:
        #USER_BPE1 = input('Username_for_BPE1: ')
        USER_BPE1 = 'USER'
        #PASSWORD_BPE1 = getpass.getpass(prompt='Password_for_BPE1:')
        PASSWORD_BPE1 = 'PASS'
        ssh.send('telnet <####IPADDR_BPE1####>\n')
        time.sleep(1)
        ssh.send(USER_BPE1 +'\n')
        time.sleep(1)
        ssh.send(PASSWORD_BPE1 + '\n')
        time.sleep(3)
        ssh.recv(1000)
        ssh.send(command_1 + '\n')
        time.sleep(3)
        result1 = ssh.recv(5000).decode('utf-8')
        unit_num_list = re.findall('unit (\d+) {', result1)
        free_unit_list =[] #создаем пустой список
        for line in range(16384):
            if str(line) not in unit_num_list:
                free_unit_list.append(str(line))
        uni = free_unit_list[4]
    #print(uni)
    #print(vardict.get('fizaddr'))
    #print(vardict.get('clientname'))
    #print(uni)
    #print(vardict.get('surms'))
    #print(DATE)
    #print(svlan)
    #print(cvlan)
    #print(cpe)
    #print(cpeport)
    #print(pp)

    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'description \"##INET,' + ' ' + vardict.get('clientname') + ', ' + 'SURMS:' + vardict.get('surms')+ ',' + ' ' + DATE + ' ' + '|' + ' ' + 'SVL:' + svlan + ' ' + 'CVL:' + cvlan + ',' + ' ' + vardict.get('fizaddr') + ' ' + '|' + ' ' + cpe + ':' + cpeport + ' ' + '|' + ' ' + 'pp' + pp + ' ' + '|' + ' ' + 'Motovilov' +' ' + '##\"')
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet rpf-check')
    resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet address' + ' ' + vardict.get('ipad') + vardict.get('ipmask'))
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'vlan-tags outer' + ' ' + svlan)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'vlan-tags inner' + ' ' + cvlan)
#resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet rpf-check')
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet policer input ' +  bw)
resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet policer output ' +  bw)
#resultlist.append('set interfaces' + ' ' + interf + ' ' + 'unit' + ' ' + uni + ' ' + 'family inet address' + ' ' + vardict.get('ipad') + vardict.get('ipmask'))
print('\n'.join(resultlist))       

