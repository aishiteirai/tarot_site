import random
import json  # NOVO: Importa a biblioteca para trabalhar com JSON
from flask import Flask, render_template, jsonify, request, url_for

app = Flask(__name__)

def carregar_significados():
    """Carrega os significados das cartas do arquivo JSON."""
    try:
        # Abre o arquivo JSON que está na pasta static/json
        with open('static/json/shortmeaning.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            # Cria um dicionário para acesso rápido usando o nome da carta como chave
            # Ex: {'aceofcups': {'description_straight': '...', 'description_upsd': '...'}, ...}
            return {carta['name']: carta for carta in dados['cartas']}
    except FileNotFoundError:
        print("AVISO: O arquivo 'shortmeaning.json' não foi encontrado. Os significados não serão carregados.")
        return {}
    except Exception as e:
        print(f"Erro ao carregar ou processar o JSON: {e}")
        return {}


# --- DADOS DO BARALHO ---

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

# --- MODIFICADO: CONSTRUÇÃO DO BARALHO ---
# Carrega os significados do JSON uma vez quando o app inicia
significados_cartas = carregar_significados()
BARALHO_COMPLETO = []

for display_name, file_name_base in CARTA_MAPPER.items():
    # Pega o significado correspondente do dicionário que carregamos
    significado = significados_cartas.get(file_name_base, {})

    BARALHO_COMPLETO.append({
        "nome": display_name,
        "imagem": f"{file_name_base}.jpeg",  # Ajustei para .png como na etapa anterior
        # Adiciona os significados ao objeto da carta, com um valor padrão caso não encontre
        "significado_normal": significado.get('description_straight', 'Significado não encontrado.'),
        "significado_invertido": significado.get('description_upsd', 'Significado não encontrado.')
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
            return jsonify({'erro': f'Número de cartas inválido.'}), 400

        baralho_embaralhado = BARALHO_COMPLETO[:]
        random.shuffle(baralho_embaralhado)

        cartas_tiradas = baralho_embaralhado[:num_cartas]

        resultado = []
        for carta_obj in cartas_tiradas:
            invertida = random.random() < 0.02

            # MODIFICADO: Escolhe o significado com base na orientação da carta
            if invertida:
                significado_final = carta_obj['significado_invertido']
            else:
                significado_final = carta_obj['significado_normal']

            resultado.append({
                'nome': carta_obj['nome'],
                'imagem': url_for('static', filename=f'images/{carta_obj["imagem"]}'),
                'invertida': invertida,
                'significado': significado_final  # NOVO: Envia o significado para o frontend
            })

        return jsonify(resultado)

    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'erro': f'Dados inválidos enviados: {e}'}), 400

@app.route('/all_cards')
def all_cards():
    """Esta função renderiza a página com a lista de todas as cartas."""
    # O BARALHO_COMPLETO já tem todos os dados que precisamos.
    # Vamos apenas passá-lo para um novo template chamado 'todas_as_cartas.html'.
    return render_template('all_cards.html', baralho=BARALHO_COMPLETO)

if __name__ == '__main__':
    app.run(debug=True)