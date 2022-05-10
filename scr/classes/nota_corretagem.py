from decimal import Decimal as dbl

class NotaCorretagem:
    Numero = ''
    Data = ''
    Corretora = ''
    Cliente = ''
    Operacoes = []

    def __init__(self) -> None:
        self.Operacoes =[]


class Operacao:
    CV = ''
    #TipoDeMercado = '' --- verificar a necessidade de dizer se a compra foi no fracionado ou foi a vista
    Papel = ''
    Quantidade = ''
    Preco = ''

    def __init__(self) -> None:
        self.CV = ''
        self.Papel = ''
        self.Quantidade = ''
        self.Preco = ''

    def str(self) -> str:
        texto = ''
        if self.CV == 'C':
            texto = 'Compra de '
        elif self.CV == 'V':
            texto = 'Venda de '
        else:
            texto = "Operação não identificada de "

        texto += self.Quantidade + ' do ' + self.Papel + ' a R$' + self.Preco + ' com um total de: R$' + str(dbl(self.Quantidade) * dbl(self.Preco.replace(',', '.')))
        print(texto)