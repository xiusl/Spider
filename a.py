# coding=utf-8
# author:xsl



with open('./oids.txt') as f:
    a = f.read()
    a = a.replace(' ', '')
    d = a.split(',')
    e = [ x[1:-1] for x in d]
    print(e)
