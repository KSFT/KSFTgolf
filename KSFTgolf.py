import sys, copy
import numpy

code=open(sys.argv[1]).read()
stack_=[]
block_cmds="iwr"
last_if=False
class obj:
    def __init__(self,o):
        if type(o)==tuple:
            self.o=list(o)
        else:
            self.o=o
    def get(self,astype):
        if astype in (int,long,float):
            if type(self.o) in (int,long,float):
                return self.o
            if type(self.o) in (str,unicode):
                try:
                    return int(self.o)
                except ValueError:
                    raise ValueError("cannot convert \""+self.o+"\" to int")
            if type(self.o) == list:
                return len(self.o)
            if type(self.o) == bool:
                return 1 if self.o else 0
        if astype in (str,unicode):
            if type(self.o) in (int,long,float):
                return str(int(self.o) if self.o == int(self.o) else self.o)
            if type(self.o) in (str,unicode):
                return self.o
            if type(self.o) == list:
                return str(self.o)
            if type(self.o) == bool:
                if self.o:
                    return "1"
                else:
                    return "0"
        if astype == list:
            if type(self.o) in (int,long,float):
                return range(int(self.o))
            if type(self.o) in (str,unicode):
                return list(self.o)
            if type(self.o) == list:
                return self.o
            if type(self.o) == bool:
                return [self]
        if astype == bool:
            return bool(self)
    def __str__(self):
        return self.get(str)
    def __nonzero__(self):
        return bool(self.o)
def parse_str_from(stack,c,i):
    ip=i
    while ip<len(c) and c[ip]!=";":
        if c[ip] in "0123456789ABCDEF":
            stack.append(obj("0123456789ABCDEF".find(c[ip])))
        elif c[ip]==":":
            stack.append(copy.deepcopy(stack[-1]))
        elif c[ip]=="'":
            stack.append(obj(c[ip+1]))
            ip+=1
        elif c[ip]=="+":
            a=stack.pop().get(int)
            b=stack.pop().get(int)
            stack.append(obj(a+b))
        elif c[ip]=="-":
            a=stack.pop().get(int)
            b=stack.pop().get(int)
            stack.append(obj(b-a))
        elif c[ip]=="*":
            a=stack.pop().get(int)
            b=stack.pop().get(int)
            stack.append(obj(a*b))
        elif c[ip]=="/":
            a=stack.pop().get(int)
            b=stack.pop().get(int)
            stack.append(obj(b/a))
        elif c[ip]=="x":
            stack.pop()
        elif c[ip]=="_":
            a=stack.pop().get(list)
            b=c[ip+1]
            d=[]
            for i in range(len(a)):
                stack.append(obj(a[i]))
                ip_=parse_str_from(stack,c,ip+1)
                d.append(stack.pop())
            ip=ip_
            stack.append(obj(d))
        elif c[ip]=="\\":
            stack[-1],stack[-2]=stack[-2],stack[-1]
        elif c[ip]=="!":
            stack.append(obj(not stack.pop().get(bool)))
        elif c[ip]==".":
            a=stack.pop().get(str)
            b=stack.pop().get(str)
            stack.append(obj(b+a))
        elif c[ip]=="h":
            stack.append(obj(100))
        elif c[ip]=="M":
            stack.append(obj(1000000))
        elif c[ip]=="t":
            stack.append(obj(1000))
        elif c[ip]=="b":
            a=stack.pop().get(int)
            b=stack.pop().get(int)
            stack.append(obj(numpy.base_repr(b,a)))
        elif c[ip]=="n":
            a=stack.pop().get(int)
            stack.append(obj(bin(a)[2:]))
        elif c[ip]=="o":
            a=stack.pop().get(str)
            b=[]
            for i in a:
                b.append(obj(ord(i)))
            stack.append(obj(b))
        elif c[ip]=="c":
            a=stack.pop().get(int)
            stack.append(obj(chr(i)))
        elif c[ip]=="q":
            stack.append(obj(input()))
        elif c[ip]=="e":
            a=stack.pop().get(int)
            b=stack.pop().get(int)
            stack.append(obj(b**a))
        elif c[ip]=="p":
            sys.stdout.write(stack[-1].get(str))
        elif c[ip]=="P":
            sys.stdout.write(stack[-1].get(str)+"\n")
        elif c[ip]==u"\u2603":
            sys.stdout.write(c)
        elif c[ip]=="m":
            x=stack.pop().get(int)
            if x<2:
                stack.append(obj(False))
            else:
                isPrime=True
                for i in range(2,x):
                    if not x%i:
                        isPrime=False
                        break
                stack.append(obj(isPrime))
            #stack.append(chr(1) if ord(stack[-1])>1 and all([ord(stack[-1])%j!=0 for j in range(2,ord(stack[-1]))]) else chr(0))
        elif c[ip]=="w":
            while stack.pop():
                ip_=parse_str_from(stack,c,ip+1)
            ip=ip_
        elif c[ip]=="i":
            if stack.pop().get(bool):
                last_if=True
                ip=parse_str_from(stack,c,ip+1)
            else:
                last_if=False
                nest_count=0
                ip+=1
                while ip<len(c) and not (nest_count==0 and c[ip]==";"):
                    if c[ip] in block_cmds:
                        nest_count+=1
                    if c[ip]==";":
                        nest_count-=1
                    ip+=1
        elif c[ip]=="l":
            if not last_if:
                ip=parse_str_from(stack,c,ip+1)
            else:
                nest_count=0
                ip+=1
                while not ((nest_count==0 and c[ip]==";") or ip>=len(c)):
                    if c[ip] in block_cmds:
                        nest_count+=1
                    if c[ip]==";":
                        nest_count-=1
                    ip+=1
        elif c[ip]=="r":
            for j in range(stack.pop().get(int)):
                stack.append(obj(j))
                ip_=parse_str_from(stack,c,ip+1)
            ip=ip_
        elif c[ip]=="a":
            for j in stack.pop().get(list):
                stack.append(j)
                ip_=parse_str_from(stack,c,ip+1)
            ip=ip_
        ip+=1
    return ip
def parse_from(i):
    parse_str_from(stack_,code,i)
def parse_str(stack,x):
    parse_str_from(stack,x,0)
stack_.append(obj(input()))
parse_from(0)
print(" ".join([i.get(str) for i in stack_]))
