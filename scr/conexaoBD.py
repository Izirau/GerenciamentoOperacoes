from multiprocessing import Event
import mysql.connector # type: ignore
from mysql.connector import errorcode # type: ignore
 
def EnviaComandoDataBase(comando, bd):
    connection = mysql.connector.connect(host = 'localhost',
                                        database= bd,
                                        user = 'root',
                                        password = 'PassSenha1!')
   
    if connection.is_connected():
        if comando != '':
            cursor = connection.cursor()
            try:
                cursor.execute(comando)
            except mysql.Error as e:
                print(e)

            connection.commit()
            cursor.close()

        connection.close()
        return True

    else:
        return False
        

def TransformaDataParaSQL(data):
    pedacos = data.split('/')
    return pedacos[2] + '-' + pedacos[1] + '-' + pedacos[0]

    
# def testes():
#     comand = 'INSERT INTO operacoes(User) VALUES("PEDRO")'
#     bd = 'operacoes_abertas'
#     print('comando enviando')
#     EnviaComandoDataBase(comand, bd)


# testes()