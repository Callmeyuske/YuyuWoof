import os

PASTA_SAIDA = "audios_sessao"
ATOR_ATUAL = "Antonio"

# Opcoes: "Adventure" ou "SinglePosts"
MODO_GERACAO = "SinglePosts"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_FUNDO = os.path.join(BASE_DIR, "assets", "fundo.gif") 

FALAS = [
    "O Senhor é meu pastor e nada me faltará.",
    "Ainda que eu ande pelo vale da sombra da morte, não temerei mal algum.",
    "Tudo posso naquele que me fortalece."
]