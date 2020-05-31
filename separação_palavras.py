import re 

stop1 = ['é']


splitter = re.compile('\\W+')
lista_palavras = []
lista = [p for p in splitter.split('Este lugar é apavorante a b c c++') if p != '']
for p in lista:
    if p not in stop1:
        lista_palavras.append(p)