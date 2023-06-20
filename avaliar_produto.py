from textblob import TextBlob
import matplotlib.pyplot as plt
from googletrans import Translator
import requests
from bs4 import BeautifulSoup

def percentage(parte, total):
    return 100 * float(parte) / float(total)

positivo = 0
negativo = 0
neutro = 0
polaridade = 0

def extrair_avaliacoes_amazon(url):
    # Faz a solicitação HTTP para a página do produto na Amazon
    response = requests.get(url)

    # Verifica se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Analisa o HTML da página usando BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontra todos os elementos de avaliação na página
        avaliacoes = soup.find_all('div', {'data-hook': 'review'})

        # Extrai o texto completo de cada avaliação
        avaliacoes_completas = []
        for avaliacao in avaliacoes:
            texto_avaliacao = avaliacao.find('span', {'data-hook': 'review-body'}).text
            avaliacoes_completas.append(texto_avaliacao)

        # Retorna as avaliações completas como uma lista
        return avaliacoes_completas

    else:
        print('Não foi possível acessar a página do produto.')
        return []


# Exemplo de uso
url_produto = 'https://www.amazon.com.br/Adaptador-Ethernet/product-reviews/B086WCG4SR/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'

avaliacoes = []
avaliacoes = extrair_avaliacoes_amazon(url_produto)


if avaliacoes:
    print('Avaliações encontradas:')
    translator = Translator()  # Inicializa o objeto Translator
    translations = []  # Lista para armazenar as traduções
    for avaliacao in avaliacoes:
        print('-' * 40)
        print(avaliacao)
        translation = translator.translate(avaliacao, dest='en').text
        translations.append(translation)
        blob = TextBlob(translation)

        polaridade += blob.sentiment.polarity
        print(translation, "\n", blob.sentiment.polarity)

        if blob.sentiment.polarity >= 0.16:
            positivo += 1
        elif blob.sentiment.polarity <= -0.20:
            negativo += 1
        else:
            neutro += 1

    positivo = format(percentage(positivo, len(avaliacoes)), '.2f')
    negativo = format(percentage(negativo, len(avaliacoes)), '.2f')
    neutro = format(percentage(neutro, len(avaliacoes)), '.2f')

    labels = ['Positivo [' + str(positivo) + '%]', 'Neutro [' + str(neutro) + '%]', 'Negativo [' + str(negativo) + '%]']
    sizes = [positivo, neutro, negativo]
    colors = ['green', 'lightgray', 'red']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)

    plt.legend(patches, labels, loc="best")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
else:
    print('Nenhuma avaliação encontrada.')
