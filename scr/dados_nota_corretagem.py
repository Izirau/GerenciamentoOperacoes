import classes.nota_corretagem as nc
import conexaoBD
import variaveis_globais as vg

def nota_corretagem_clear(dic_lines = {}):
        #cria uma lista de todos os textos ordenados pelo valor de y
        lista_valores_pagina = list(dic_lines.values())

        linha_numero_nota = nc.NotaCorretagem()

        for i in range(len(dic_lines)):
            
            valores_da_linha = lista_valores_pagina[i]            
            valores_da_linha_seguinte = ''
            valores_da_linha_seguinte_2 = ''
            if i + 1 < len(dic_lines):
                valores_da_linha_seguinte = lista_valores_pagina[i+1]

            if i + 2 < len(dic_lines):
                valores_da_linha_seguinte_2 = lista_valores_pagina[i+2]
            
            #print(valores_da_linha[0].texto.strip().upper())

            if valores_da_linha[0].texto.strip().upper() == 'NR. NOTA':                
                linha_numero_nota.Numero = valores_da_linha_seguinte[0].texto.strip()
                linha_numero_nota.Data = valores_da_linha_seguinte[2].texto.strip()
                linha_numero_nota.Corretora = valores_da_linha_seguinte_2[0].texto.strip()

            if valores_da_linha[0].texto.strip().upper() == 'CLIENTE':
                linha_numero_nota.Cliente = valores_da_linha_seguinte[0].texto
            
            if valores_da_linha[0].texto.strip().upper() == 'Q NEGOCIACAO' or valores_da_linha[0].texto.strip().upper() == 'Q NEGOCIAÇÃO':
                operacoes = valores_da_linha_seguinte #pega o valor da primeira operação
                j = 0 #gera um iterador para poder pegar a próxima nota
                #itera até encontrar o resumo financeiro, é isso que diz que acabaram as operações daquela nota
                while operacoes[0].texto.strip().upper() != 'RESUMO FINANCEIRO':
                    campos = len(operacoes)
                    op = nc.Operacao()
                    if campos == 6:
                        op.CV = operacoes[1].texto.strip().split(' ')[0]
                        op.Papel = operacoes[2].texto.strip()
                        op.Quantidade = operacoes[3].texto.strip()
                        op.Preco = operacoes[4].texto.strip()
                    elif campos == 7:
                        #caso onde a adição é na coluna de observação
                        op.CV = operacoes[1].texto.strip().split(' ')[0]
                        op.Papel = operacoes[2].texto.strip()
                        op.Quantidade = operacoes[4].texto.strip()
                        op.Preco = operacoes[5].texto.strip()
                    else:
                        print("Leitura operações: Erro na quantidade de campos da operação {0}".format(j + 1))
                        vg.erro_leitura_nota = True


                    linha_numero_nota.Operacoes.append(op)
                    #faz a leitura da próxima operação
                    j += 1            
                    operacoes = lista_valores_pagina[i + 1 + j]
        

        # print('Número da nota de corretagem = ' + linha_numero_nota.Numero)
        # print('Data da nota de corretagem = ' + linha_numero_nota.Data)
        # print('Corretora da nota = ' + linha_numero_nota.Corretora)
        # print('Cliente = '+ linha_numero_nota.Cliente)

        for operacao in range(len(linha_numero_nota.Operacoes)):
            linha_numero_nota.Operacoes[operacao].str()

            comando = 'INSERT INTO operacoes(NoteNumber, Date, Corretora, User, CV, Papel, Quantidade, Preço) VALUES ("' + \
            linha_numero_nota.Numero + '","' + conexaoBD.TransformaDataParaSQL(linha_numero_nota.Data) + '","' + linha_numero_nota.Corretora + '","' + linha_numero_nota.Cliente + '","' + \
            linha_numero_nota.Operacoes[operacao].CV + '","' + linha_numero_nota.Operacoes[operacao].Papel + '","' + \
            linha_numero_nota.Operacoes[operacao].Quantidade  + '","' + linha_numero_nota.Operacoes[operacao].Preco.replace(',','.') + '")'
            #print(comando)
            #bd = 'operacoes_abertas'
            print('comando enviando')
            conexaoBD.EnviaComandoDataBase(comando, 'operacoes_abertas')   