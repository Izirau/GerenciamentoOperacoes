from io import BytesIO
from types import NoneType
import os.path
import sys
import variaveis_globais as vg
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter # type: ignore
from pdfminer.layout import LAParams # type: ignore
from pdfminer.pdfdocument import PDFDocument # type: ignore
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter # type: ignore
from pdfminer.pdfpage import PDFPage # type: ignore
from pdfminer.pdfparser import PDFParser # type: ignore
import xml.etree.ElementTree as eletree
from classes.location import localizacao
from classes.nota_corretagem import NotaCorretagem
from classes.nota_corretagem import Operacao
from decimal import Decimal as dbl
import dados_nota_corretagem
import conexaoBD

# def ler_arquivo(caminho):
#     output_string = io.StringIO() # type: ignore
#     with open(caminho, 'rb') as in_file:
#         parser = PDFParser(in_file)
#         doc = PDFDocument(parser)
#         rsrcmgr = PDFResourceManager()
#         device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#         interpreter = PDFPageInterpreter(rsrcmgr, device)
#         for page in PDFPage.create_pages(doc):
#             interpreter.process_page(page)

#     print(output_string.getvalue())

#Converte o PDF para XML
def convert_pdf(path, format='text', codec='utf-8', password=''):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()

    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    print("Log: Arquivo convertido")
    return text

#Converte as linhas text abaixo de textline para somente uma linha
def compila_text_line(xml_as_text):
    raiz = eletree.fromstring(xml_as_text)
    filtro = "*"
    contador = 0    
    
    for child in raiz.iter(filtro):
        #contador+=1
        if child.tag == 'textline':
            texto = ''
            quantidade = 0
            for filho in child.iter(filtro):
                if filho.tag == 'textline': continue

                #para cada linha que tem texto é adicionado o valor do texto da linha na variável e 
                #um valor no contador quantidade, para posteriormente saber quantas linhas precisam ser removidas
                #do xml
                if filho.tag == 'text':
                    quantidade += 1
                    if filho.text != None:
                        texto += filho.text
                    else:
                        texto += " "
                else:
                    break
            
            #remove as linhas do xml
            for i in range(quantidade) :
                child.remove(child[0])

            #por causa do codex é necessário fazer uma conversão para tirar os caracteres não reconhecidos
            texto = arruma_texto(texto)

            #readiciona o texto como um elemento text abaixo do textline
            sub_element =  eletree.SubElement(child,"text")
            sub_element.text = texto
    print("Log: Texto corrigido")
    return raiz
    
def arruma_texto(texto):
    texto = texto.replace("NEGOCIA��O", 'NEGOCIACAO')
    texto = texto.replace("preg�o",'pregao')
    texto = texto.replace("29� ANDAR",'29o ANDAR')
    texto = texto.replace("C�digo",'Codigo')
    texto = texto.replace("Ag�ncia",'Agencia')
    texto = texto.replace('Neg�cio', 'Negocio')
    texto = texto.replace('Negocia��o', 'Negociacao')
    texto = texto.replace('Opera��o', 'Operacao')
    texto = texto.replace('Especifica��o', 'Especificacao')
    texto = texto.replace("t�tulo", 'titulo')
    texto = texto.replace("Pre�o", 'Preco')
    texto = texto.replace("�quido", 'iquido')
    texto = texto.replace("opera��es", 'operacoes')
    texto = texto.replace("op��es", 'opcoes')
    texto = texto.replace("Execu��o", 'Execucao')
    texto = texto.replace("Cust�dia", 'Custodia')
    texto = texto.replace('iquida��o', 'iquidacao')
    texto = texto.replace('Deb�ntures', 'Debentures')
    texto = texto.replace('� vista', 'a vista')
    texto = texto.replace('Op��es', 'Opcoes')
    texto = texto.replace('Opera��es', 'Operacoes')
    texto = texto.replace('� termo', 'a termo')
    texto = texto.replace("p�bl.", 'publ.')
    texto = texto.replace('Especifica��es', 'Especificacoes')
    texto = texto.replace('Pr�pria', 'Propria')
    texto = texto.replace('Precat�rio', 'Precatorio')
    texto = texto.replace('Posi��o', 'Posicao')
    texto = texto.replace('A��es', 'Acoes')
    texto = texto.replace('Observa��o', 'Observacao')
    texto = texto.replace('n�o s�o', 'nao sao')
    texto = texto.replace('regi�es', 'regioes')
    texto = texto.replace('Observa��es', 'Observacoes')

    return texto

def posicionamento(arquivo):
    #cria um dicionário com a chave sendo o y inicial a chave e o valor é um objeto localização
    raiz = arquivo
    filtro = 'page'

    dic_lines = {}

    #lista_paginas = []

    filtro = 'page' # para iterar uma página de cada vez  

    for pagina in raiz.iter(filtro):
        vg.erro_leitura_nota = False
        filtro = 'textline'
        dic_lines.clear()
        for child in pagina.iter(filtro):
            coordenadas = child.get('bbox').split(',') #bbox é o valor om x_inicial, y_inicial, x_final, y_final
            cord = localizacao(coordenadas[0], coordenadas[1], coordenadas[2], coordenadas[3])
            cord.texto = child.find('text').text 

            y_dbl = dbl(coordenadas[1]) #y como double (para poder ordenar)
            if y_dbl in dic_lines.keys():
                dic_lines[y_dbl].append(cord)
            else:
                dic_lines[y_dbl] = [cord]
        
        #ordenação inversa pois o x=0 e y=0 ficam na ponta inferior esquerda, aumentando para cima e pra a direita
        #ou seja, a primeira linha de cima é o maior valor de y.
        dic_lines = dict(sorted(dic_lines.items(), reverse = True))
        #trata a nota de corretagem da clear - por enquanto a única testada
        dados_nota_corretagem.nota_corretagem_clear(dic_lines)          

if __name__ == '__main__':
    
    global bd
    bd = 'operacoes_abertas'

    arquivo = '../GerenciaOperacoes_old/NotasCorretagem/88650_NotaCorretagem 01-11-2020 a 31-12-2020.pdf'

    if not os.path.exists(arquivo):
        print("Error: Arquivo '{0}' não encontrado".format(arquivo))
        sys.exit()
    else:
        print("Log: Arquivo encontrado")

    if not conexaoBD.EnviaComandoDataBase('', bd):
        print("Error: Conexão com banco de dados falhou")
        sys.exit()
    else:
        print("Log: Conexão com o banco de dados com sucesso")
    
    
    xml = convert_pdf(arquivo, 'xml') + '</pages>'
    xml_tratado = compila_text_line(xml)    
    posicionamento(xml_tratado)
