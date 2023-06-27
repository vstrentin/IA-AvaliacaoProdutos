from flask import Flask, render_template, request
import matplotlib
from textblob import TextBlob
import matplotlib.pyplot as plt
matplotlib.use('agg')
from googletrans import Translator
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
retry_count = 0

def percentage(parte, total):
    return 100 * float(parte) / float(total)

def extrair_avaliacoes_amazon(url):
    global retry_count  # Adiciona a declaração global para modificar a variável retry_count dentro da função
    response = requests.get(url)

    if response.status_code == 200:
        print('Solicitação bem-sucedida')
        soup = BeautifulSoup(response.content, 'html.parser')
        avaliacoes = soup.find_all('div', {'data-hook': 'review'})
        avaliacoes_completas = []
        for avaliacao in avaliacoes:
            texto_avaliacao = avaliacao.find('span', {'data-hook': 'review-body'}).text
            avaliacoes_completas.append(texto_avaliacao)
        return avaliacoes_completas
    
    elif response.status_code == 503:
        max_retries = 5  # Número máximo de tentativas
        retry_delay = 5  # Tempo de espera entre as tentativas (em segundos)

        if retry_count < max_retries:
            retry_count += 1
            print('Serviço indisponível, tentando novamente em', retry_delay, 'segundos...')
            print(retry_count)
            time.sleep(retry_delay)
            return extrair_avaliacoes_amazon(url)
        else:
            print('Limite máximo de tentativas atingido. Não foi possível extrair as avaliações.')
            retry_count = 0  # Reinicia a variável retry_count para zero após atingir o limite máximo de tentativas
            return []
    
    else:
        print('Solicitação mal-sucedida. Código de status:', response.status_code)
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
        plt.savefig('C:\\Users\\Eduar\\OneDrive\\Documentos\\Projetos\\Faculdade\\IA-AvaliacaoProdutos\\com site\\static\\grafico.png')
        plt.close()

        most_positive = avaliacoes[sentimentos.index(max(sentimentos))]
        most_negative = avaliacoes[sentimentos.index(min(sentimentos))]

        return translations, avaliacoes, most_positive, most_negative
    else:
        return [], [], '', ''


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_produto = request.form['url_produto']
        translations, avaliacoes, most_positive, most_negative = analisar_avaliacoes(url_produto)
        return render_template('result.html', translations=translations, avaliacoes=avaliacoes, most_positive=most_positive, most_negative=most_negative)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
