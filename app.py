import random
from flask import Flask, render_template, jsonify, request, url_for  # Importe url_for

app = Flask(__name__)


# --- DADOS DO BARALHO ---

# Helper para gerar nomes de arquivos (se você tiver um padrão específico)
# Assumimos que as imagens são .jpg e os nomes seguem um padrão como "aceofcups.jpg"
def gerar_nome_arquivo(nome_carta):
    # Converte o nome da carta para minúsculas e remove espaços para o nome do arquivo
    # Ex: "O Louco" -> "olouco", "Ás de Paus" -> "asdepaus"
    nome_formatado = nome_carta.lower().replace(" ", "").replace("á", "a").replace("é", "e").replace("í", "i").replace(
        "ó", "o").replace("ú", "u").replace("ç", "c")
    return f"{nome_formatado}.jpg"  # Assumindo que todas as suas imagens são .jpg


# Lista completa com os 78 arcanos do Tarot de Rider-Waite
# Cada carta será um dicionário para armazenar nome e nome do arquivo de imagem
ARCANOS_MAIORES_NOMES = [
    "O Louco", "O Mago", "A Sacerdotisa", "A Imperatriz", "O Imperador",
    "O Hierofante", "Os Amantes", "A Carruagem", "A Justiça", "O Eremita",
    "A Roda da Fortuna", "A Força", "O Enforcado", "A Morte", "A Temperança",
    "O Diabo", "A Torre", "A Estrela", "A Lua", "O Sol", "O Julgamento", "O Mundo"
]

# Notei que seus arquivos seguem o padrão "aceofcups", "twoofswords", etc.
# É importante que a lista de cartas e os nomes dos arquivos correspondam.
# Vou usar uma versão mais próxima dos nomes dos seus arquivos para mapeamento.
# Adapte esta lista para que os nomes 'key' correspondam exatamente aos seus nomes de arquivo,
# e 'display' seja como você quer que apareça na tela (opcional, mas bom para legendas).

# Mapeamento do nome de exibição para o nome do arquivo (sem extensão)
CARTA_MAPPER = {
    "O Louco": "thefool", "O Mago": "themagician", "A Sacerdotisa": "thehighpriestess",
    "A Imperatriz": "theempress", "O Imperador": "theemperor", "O Hierofante": "thehierophant",
    "Os Amantes": "thelovers", "A Carruagem": "thechariot", "A Justiça": "justice",
    "O Eremita": "thehermit", "A Roda da Fortuna": "wheeloffortune", "A Força": "thestrength",
    "O Enforcado": "thehangedman", "A Morte": "death", "A Temperança": "temperance",
    "O Diabo": "thedevil", "A Torre": "thetower", "A Estrela": "thestar", "A Lua": "themoon",
    "O Sol": "thesun", "O Julgamento": "judgement", "O Mundo": "theworld",

    "Ás de Paus": "aceofwands", "Dois de Paus": "twoofwands", "Três de Paus": "threeofwands",
    "Quatro de Paus": "fourofwands", "Cinco de Paus": "fiveofwands", "Seis de Paus": "sixofwands",
    "Sete de Paus": "sevenofwands", "Oito de Paus": "eightofwands", "Nove de Paus": "nineofwands",
    "Dez de Paus": "tenofwands", "Pajem de Paus": "pageofwands", "Cavaleiro de Paus": "knightofwands",
    "Rainha de Paus": "queenofwands", "Rei de Paus": "kingofwands",

    "Ás de Copas": "aceofcups", "Dois de Copas": "twoofcups", "Três de Copas": "threeofcups",
    "Quatro de Copas": "fourofcups", "Cinco de Copas": "fiveofcups", "Seis de Copas": "sixofcups",
    "Sete de Copas": "sevenofcups", "Oito de Copas": "eightofcups", "Nove de Copas": "nineofcups",
    "Dez de Copas": "tenofcups", "Pajem de Copas": "pageofcups", "Cavaleiro de Copas": "knightofcups",
    "Rainha de Copas": "queenofcups", "Rei de Copas": "kingofcups",

    "Ás de Espadas": "aceofswords", "Dois de Espadas": "twoofswords", "Três de Espadas": "threeofswords",
    "Quatro de Espadas": "fourofswords", "Cinco de Espadas": "fiveofswords", "Seis de Espadas": "sixofswords",
    "Sete de Espadas": "sevenofswords", "Oito de Espadas": "eightofswords", "Nove de Espadas": "nineofswords",
    "Dez de Espadas": "tenofswords", "Pajem de Espadas": "pageofswords", "Cavaleiro de Espadas": "knightofswords",
    "Rainha de Espadas": "queenofswords", "Rei de Espadas": "kingofswords",

    "Ás de Ouros": "aceofpentacles", "Dois de Ouros": "twoofpentacles", "Três de Ouros": "threeofpentacles",
    "Quatro de Ouros": "fourofpentacles", "Cinco de Ouros": "fiveofpentacles", "Seis de Ouros": "sixofpentacles",
    "Sete de Ouros": "sevenofpentacles", "Oito de Ouros": "eightofpentacles", "Nove de Ouros": "nineofpentacles",
    "Dez de Ouros": "tenofpentacles", "Pajem de Ouros": "pageofpentacles", "Cavaleiro de Ouros": "knightofpentacles",
    "Rainha de Ouros": "queenofpentacles", "Rei de Ouros": "kingofpentacles",
}

# Constrói o baralho completo com informações de imagem
BARALHO_COMPLETO = []
for display_name, file_name_base in CARTA_MAPPER.items():
    BARALHO_COMPLETO.append({
        "nome": display_name,
        "imagem": f"{file_name_base}.jpeg"  # Nome do arquivo da imagem
    })


# --- ROTA PRINCIPAL (INTERFACE) ---
@app.route('/')
def home():
    return render_template('index.html')


# --- ROTA DA LÓGICA (API) ---
@app.route('/tirar-cartas', methods=['POST'])
def tirar_cartas():
    try:
        dados = request.get_json()
        num_cartas = int(dados['quantidade'])

        if not 1 <= num_cartas <= len(BARALHO_COMPLETO):
            return jsonify({'erro': f'Número de cartas inválido. Escolha entre 1 e {len(BARALHO_COMPLETO)}.'}), 400

        baralho_embaralhado = BARALHO_COMPLETO[:]
        random.shuffle(baralho_embaralhado)

        cartas_tiradas = baralho_embaralhado[:num_cartas]

        resultado = []
        for carta_obj in cartas_tiradas:
            invertida = random.random() < 0.02

            resultado.append({
                'nome': carta_obj['nome'],
                'imagem': url_for('static', filename=f'images/{carta_obj["imagem"]}'),
                # Gera o URL correto para a imagem
                'invertida': invertida
            })

        return jsonify(resultado)

    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'erro': f'Dados inválidos enviados: {e}'}), 400


if __name__ == '__main__':
    app.run(debug=True)