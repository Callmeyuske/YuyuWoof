import os

PASTA_SAIDA = "audios_sessao"
ATOR_ATUAL = "Antonio"

# Opcoes: "Adventure" ou "SinglePosts"
MODO_GERACAO = "SinglePosts"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_FUNDO = os.path.join(BASE_DIR, "assets", "fundo.mp4") 

FALAS = [
    "Salmo 91. Aquele que habita no esconderijo do Altíssimo, à sombra do Onipotente descansará. Direi do Senhor: Ele é o meu refúgio, a minha fortaleza, e nele confiarei."
]