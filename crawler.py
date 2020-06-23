import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import nltk
import pymysql

def inserePalavraLocalizacao(idurl, idpalavra, localizacao):
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*', db='indice', autocommit = True)
    cursor = conexao.cursor()
    cursor.execute('insert into palavra_localizacao (idurl, idpalavra, localizacao) values (%s, %s, %s)', (idurl, idpalavra, localizacao))
    idpalavra_localizacao = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idpalavra_localizacao


def inserePalavra(palavra):
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    cursor.execute('insert into palavras (palavra) values (%s)', palavra)
    idpalavra = cursor.lastrowid 
    cursor.close()
    conexao.close()
    return idpalavra
    

def palavraIndexada(palavra):
    retorno = -1 #não existe a palavra no indice
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*', db='indice', use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    cursor.execute('select idpalavra from palavras where palavra = %s', palavra)
    if cursor.rowcount > 0:
        #print("Palavra já cadastrada")
        retorno = cursor.fetchone()[0]
    #else:
        #print("Palavra não cadastrada")
    cursor.close()
    conexao.close()
    return retorno


def inserePagina(url):
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*', db='indice', autocommit = True)
    cursor = conexao.cursor()
    cursor.execute('insert into urls (url) values (%s)', url)
    idpagina = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idpagina


def paginaIndexada(url):
    retorno = -1 #se retornar -1 significa que não existe a página.
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*', db='indice')
    cursorUrl = conexao.cursor()
    cursorUrl.execute('select idurl from urls where url = %s', url)    
    if cursorUrl.rowcount > 0:
        #print("Url cadastrada")
        idurl = cursorUrl.fetchone()[0]
        cursorPalavra = conexao.cursor()
        cursorPalavra.execute('select idurl from palavra_localizacao where idurl = %s', idurl)
        if cursorPalavra.rowcount > 0:
            #print("Url com palavras")
            retorno = -2 #se retornar -2 significa que existe a página com palavras
        else:
            #print("Url sem palavras cadastradas")
            retorno = idurl #existe a página sem palavras, então retorna ID da página
        
        cursorPalavra.close()
    #else:
        #print("Url não cadastrada")
    
    cursorUrl.close()
    conexao.close()
    return retorno


def separaPalavras(texto):
    stop = nltk.corpus.stopwords.words('portuguese')
    stemmer = nltk.stem.RSLPStemmer()
    splitter = re.compile('\\W+')
    lista_palavras = []
    lista = [p for p in splitter.split(texto) if p != '']
    for p in lista:
        if p.lower() not in stop:
            if len(p) > 1:
                lista_palavras.append(stemmer.stem(p).lower())
    return lista_palavras


def getTexto(sopa):
    for tags in sopa(['script','style']):
        tags.decompose()
    return ' '.join(sopa.stripped_strings)


def indexador(url, sopa):
    indexada = paginaIndexada(url)
    if indexada == -2:
        print("URL já indexada")
        return
    elif indexada == -1:
        idnova_pagina = inserePagina(url)
    elif indexada > 0:
        idnova_pagina = indexada
    print("Indexando "+ url)
    texto = getTexto(sopa)
    palavras = separaPalavras(texto)
    for i in range(len(palavras)):
        palavra = palavras[i]
        idpalavra = palavraIndexada(palavra)
        if idpalavra == -1:
            idpalavra = inserePalavra(palavra)
        inserePalavraLocalizacao(idnova_pagina, idpalavra, i)


def crawl(paginas, profundidade):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for i in range(profundidade):
        novas_paginas = set()
        for pagina in paginas:
            http = urllib3.PoolManager()
            try:
                dados_pagina = http.request('GET', pagina)
            except:
                #print('Erro ao abrir a página',+pagina)
                continue
            sopa = BeautifulSoup(dados_pagina.data, "lxml")
            indexador(pagina, sopa)
            links = sopa.find_all('a')
            contador = 1
            for link in links:
                #print(str(link.contents)+" - "+ str(link.get('href')))
                #print(link.attrs)
                #print('\n')
                if ('href' in link.attrs):
                    url = urljoin(pagina, str(link.get('href')))
                    #if url != link.get('href'):
                    #    print(url)
                    #    print(link.get('href'))
                    if url.find("'") != -1:
                        continue
                    #print(url)
                    url = url.split('#')[0]
                    #print(url)
                    #print('\n')
                    if url[0:4] == 'http':
                        novas_paginas.add(url)
                    contador = contador + 1 
        paginas = novas_paginas                  
    print(contador)


listapaginas = ['https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o']
crawl(listapaginas, 2)