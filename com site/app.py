from flask import Flask, render_template, request
import matplotlib
from textblob import TextBlob
import matplotlib.pyplot as plt
matplotlib.use('agg')
from googletrans import Translator
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def percentage(parte, total):
    return 100 * float(parte) / float(total)

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

def analisar_avaliacoes(url_produto):
    avaliacoes = extrair_avaliacoes_amazon(url_produto)

    if avaliacoes:
        sentimentos = []
        translations = []

        translator = Translator()
        for avaliacao in avaliacoes:
            translation = translator.translate(avaliacao, dest='en').text
            translations.append(translation)
            blob = TextBlob(translation)
            sentimentos.append(blob.sentiment.polarity)

        positivo = sum(1 for sentimento in sentimentos if sentimento >= 0.16)
        negativo = sum(1 for sentimento in sentimentos if sentimento <= -0.20)
        neutro = sum(1 for sentimento in sentimentos if -0.20 < sentimento < 0.16)

        total_avaliacoes = len(avaliacoes)
        positivo_percent = format(percentage(positivo, total_avaliacoes), '.2f')
        negativo_percent = format(percentage(negativo, total_avaliacoes), '.2f')
        neutro_percent = format(percentage(neutro, total_avaliacoes), '.2f')       


        labels = ['Positivo [' + str(positivo_percent) + '%]', 'Neutro [' + str(neutro_percent) + '%]', 'Negativo [' + str(negativo_percent) + '%]']
        sizes = [positivo_percent, neutro_percent, negativo_percent]
        colors = ['green', 'lightgray', 'red']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)

        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('D:/IA-AvaliacaoProdutos/com site/static/grafico.png')
        plt.close()

        return translations, avaliacoes
    else:
        return [], []


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_produto = request.form['url_produto']
        translations, avaliacoes = analisar_avaliacoes(url_produto)
        return render_template('result.html', translations=translations, avaliacoes=avaliacoes)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
