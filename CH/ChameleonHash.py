from CH.HashUtil import *

# SK = getSecretKey(q)
# PK = getPublicKey(SK, g, p)
SKlist = []
PKlist = []
SK = 9583268362935874027000375325971484198933129732104461332343913
PK = 17642134390506942541899470387315131178079445707001368818596514012034
p = 18604511303632357477261733749289932684042548414204891841229696446591
q = 2238810024504495484628367478855587567273471529988554974877219789
g = 12340


def chameleonHash(PK, m, r):
    if isinstance(m, str):
        m = str2int(m)
    return quickPower(g, m, p) * quickPower(PK, r, p) % p


def forge(SK, m1, r1, m2):
    if isinstance(m1, str):
        m1 = str2int(m1)
    if isinstance(m2, str):
        m2 = str2int(m2)
    x, y, gcd = exgcd(SK, q)
    return x * (m1 - m2 + SK * r1) % q


def chameleonHashSplit(PKlist, g, m, rlist, n):
    if isinstance(m, str):
        m = str2int(m)
        ch = quickPower(g, m, p)
        for i in range(n):
            ch = ch * quickPower(PKlist[i], rlist[i], p)
        ch = ch % p
    return ch


def forgeSplit(SKlist, m1, rlist, m2, q, i):  # find r', i is the index
    if isinstance(m1, str):
        m1 = str2int(m1)
    if isinstance(m2, str):
        m2 = str2int(m2)
    x, y, gcd = exgcd(SKlist[i], q)
    result = x * (m1 - m2 + SKlist[i] * rlist[i]) % q
    return result


if __name__ == "__main__":
    print('SCHEME 1: Centralized Setting')

    msg1 = 'i sent first message'  # 消息1
    msg2 = 'second message'  # 消息2
    newmsg1 = str2int(msg1)
    newmsg2 = str2int(msg2)
    rand1 = random.randint(1, q)  # r

    print('q =', q)
    print('p =', p)
    print('g =', g)
    print('SK =', SK)
    print('PK =', PK)
    print('')

    print('msg1 =', msg1)
    print('rand1 =', rand1)
    CH = chameleonHash(PK, g, newmsg1, rand1)
    print('CH =', CH)
    print('')

    print('msg2 =', msg2)
    rand2 = forge(SK, newmsg1, rand1, newmsg2)
    print('rand2 =', rand2)
    newCH = chameleonHash(PK, g, newmsg2, rand2)
    print('newCH =', newCH)

    print('\n\n\n\nSCHEME 2: Multiplayer Setting')

    n = 3  # five players

    SKlist, PKlist = KeyGen(p, q, g, 3)
    rlist = getr(3, q)

    msg1 = 'i sent first message'  # 消息1
    msg2 = 'second message'  # 消息2

    print('q=', q)
    print('p=', p)
    print('g=', g)
    print('SK=', SKlist)
    print('PK=', PKlist)
    print('')

    print('msg1=', msg1)
    print('r=', rlist)
    CH = chameleonHashSplit(PKlist, g, msg1, rlist, n)
    print('CH=', CH)
    print('')

    i = 2  # the second player change the message
    print('msg2=', msg2)
    rand2 = forgeSplit(SKlist, msg1, rlist, msg2, q, i)
    print('rand2=', rand2)
    rlist[i] = rand2
    newCH = chameleonHashSplit(PKlist, g, msg2, rlist, n)
    print('newCH=', newCH)
