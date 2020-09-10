import pymysql
import nltk

def getIdPalavra(palavra):
    retorno=-1
    stemmer = nltk.stem.RSLPStemmer()
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*',db='indice')
    cursor = conexao.cursor()
    cursor.execute('select idpalavra from palavras where palavra = %s', stemmer.stem(palavra))  
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return retorno

def pesquisa(consulta):
    linhas, palavraid = buscaMaisPalavras(consulta)
    scores = dict([linha[0],0] for linha in linhas)
    #for linha in linhas:
    #    print(linha[0])
    #for url, score in scores.items():
    #    print(str(url)+' - '+str(score))
    scoresordenado = sorted([(score, url)for(url,score) in scores.items()])
    for (score,idurl) in scoresordenado[0:10]:
        print('%f\t%s' % (score,getUrl(idurl)))      

def getUrl(idurl):
    retorno = ''
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*',db='indice')
    cursor = conexao.cursor()
    cursor.execute('select url from urls where idurl = %s',idurl)
    if cursor.rowcount >0:
        retorno = cursor.fetchone()[0]       
    cursor.close()
    conexao.close()
    return retorno

def buscaMaisPalavras(consulta):
    listacampos = 'p1.idurl'
    listatabelas = ''
    listaclausulas = ''
    palavrasid = []
    
    palavras = consulta.split(' ') #quebra espaços vazios em itens do vetor
    numerotabela = 1
    for palavra in palavras:
        idpalavra = getIdPalavra(palavra)
        if idpalavra > 0:
            palavrasid.append(idpalavra)
            if numerotabela > 1:
                listatabelas += ', '
                listaclausulas += ' and '
                listaclausulas += 'p%d.idurl = p%d.idurl and ' % (numerotabela -1, numerotabela)
            listacampos += ', p%d.localizacao' % numerotabela
            listatabelas += 'palavra_localizacao p%d' % numerotabela
            listaclausulas += 'p%d.idpalavra = %d' % (numerotabela, idpalavra)
            numerotabela += 1
    consultacompleta = 'select %s from %s where %s' %(listacampos, listatabelas, listaclausulas)
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*',db='indice')
    cursor = conexao.cursor()
    cursor.execute(consultacompleta)
    linhas = [linha for linha in cursor]
    
    cursor.close()
    conexao.close()
    return linhas,palavrasid
    
#linhas, palavrasid = buscaMaisPalavras('python programação')


def buscaUmaPalavra(palavra):
    idpalavra = getIdPalavra(palavra)
    conexao = pymysql.connect(host='localhost', user='root',passwd='351246Ed*',db='indice')
    cursor = conexao.cursor()
    cursor.execute('select urls.url from palavra_localizacao plc inner join urls on plc.idurl = urls.idurl where plc.idpalavra = %s', idpalavra)
    paginas = set()
    for url in cursor:
        #print(url[0])
        paginas.add(url[0])
    
    print('Páginas encontradas: ', str(len(paginas)))
    for url in paginas:
        print(url)
    cursor.close()
    conexao.close()
    
#buscaUmaPalavra('Programação')
