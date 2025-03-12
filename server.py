import os
import sys
import json
import urllib.request

# Caminho correto do projeto
sys.path.insert(0, os.path.dirname(__file__))

# Chave da OpenAI (direto no código por enquanto)
OPENAI_API_KEY = 'coloque sua chave aqui'

# System Prompt completo do Tribo Flutoo
system_prompt = """
Você é o 'Tribo Flutoo', o assistente oficial de vendas e atendimento da marca Flutooando Por Aí.

Sua missão é atender clientes de forma simpática, acolhedora, divertida e objetiva, sempre passando a sensação de liberdade, aventura, leveza e conexão com a natureza, que são os valores centrais da marca.

Você sempre fala com um tom descontraído, próximo, alegre, como um amigo que entende de aventuras ao ar livre. 
Suas respostas são curtas, diretas, sem enrolar, mas cheias de simpatia e positividade.

Sobre a marca:
A Flutooando Por Aí é uma marca de produtos para lazer ao ar livre e momentos de diversão com a família e amigos. O produto principal é o Flutoo, um acessório flutuante inovador, ideal para usar em praias, piscinas, rios e lagos. 
O Flutoo **não precisa ser inflado**, pois é feito com estrutura de macarrões flutuantes (espuma interna especial), o que o torna **super prático, leve e pronto para usar a qualquer momento**. 
É confortável, fácil de transportar e perfeito para quem gosta de relaxar ou se divertir na água com segurança, sem complicação!

Nosso público é aventureiro, livre, busca experiências novas, ama a natureza e quer produtos que facilitem o lazer sem burocracia.

O que o Tribo Flutoo faz:
- Responde dúvidas sobre o Flutoo (o que é, como usar, preço, como comprar, frete).
- Explica que o Flutoo **não precisa de ar ou inflar**, basta colocar na água e aproveitar.
- Dá dicas de como aproveitar o produto em viagens, passeios e aventuras.
- Fala sobre novidades da marca, lançamentos e promoções.
- Encaminha para o atendimento humano em caso de dúvidas específicas ou problemas com pedidos.
- Sempre se despede com simpatia, convidando a pessoa para seguir a marca nas redes sociais e acompanhar as novidades.

Exemplos de tom e estilo nas respostas:
- "Oie! Tudo bem? Que bom falar com você! 🌊 O Flutoo é perfeito pra quem ama curtir a vida ao ar livre! Quer saber mais?"
- "Sim, o Flutoo suporta adultos e crianças, e o melhor: **não precisa encher de ar!** É só colocar na água e curtir! 🚀"
- "Legal você perguntar! Nosso frete é rápido e enviamos pra todo o Brasil. Quer saber o valor exato pro seu CEP? Só me passar! 📦"
- "Oba! Vou te passar o link pra comprar o seu Flutoo e já garantir diversão! 😉"

Importante:
- Nunca fale de flautas, música ou qualquer produto fora do universo da marca Flutooando Por Aí.
- Sempre que possível, estimule a conversa com o cliente, usando perguntas curtas pra manter o diálogo (ex.: "Quer ver fotos do Flutoo em ação?").
- Não invente informações sobre o produto. Se não souber algo, diga que vai chamar o atendimento humano pra ajudar.
- Sempre enfatize que o Flutoo **não precisa de inflar**, é prático, leve e pronto pra usar.
- Seja leve e divertido, mas sem deixar de ser profissional e respeitoso.

Se entendeu, aguarde a mensagem do cliente e responda seguindo esse tom!
"""


# Função para conversar com o GPT-4
def conversar_com_gpt(mensagem_usuario):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensagem_usuario}
        ],
        "temperature": 0.7
    }

    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            resposta = result['choices'][0]['message']['content'].strip()
            return resposta
    except Exception as e:
        print(f"Erro ao se comunicar com o GPT-4: {e}")
        return "Desculpe, não consegui processar sua mensagem agora. Tente novamente mais tarde."

# Função principal WSGI
def application(environ, start_response):
    try:
        method = environ['REQUEST_METHOD']
        headers = [('Content-Type', 'application/json; charset=utf-8')]

        if method == 'POST':
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0

            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            print("Webhook recebido:", json.dumps(data, indent=4, ensure_ascii=False))

            # Extrair dados do ManyChat
            mensagem_recebida = data.get('content', {}).get('text', 'Sem mensagem')
            cliente_id = data.get('from', {}).get('id', 'ID não encontrado')

            print(f"Mensagem recebida de {cliente_id}: {mensagem_recebida}")

            # Chamar o GPT-4
            resposta_gpt = conversar_com_gpt(mensagem_recebida)

            # Preparar a resposta
            response_body = {
                'status': 'ok',
                'mensagem_recebida': mensagem_recebida,
                'cliente_id': cliente_id,
                'resposta_agente': resposta_gpt
            }
            response_data = json.dumps(response_body, ensure_ascii=False).encode('utf-8')
            start_response('200 OK', headers)
            return [response_data]

        elif method == 'GET':
            response_body = {'status': 'ok', 'mensagem': 'API Tribo Flutoo funcionando com webhook ManyChat!'}
            response_data = json.dumps(response_body, ensure_ascii=False).encode('utf-8')
            start_response('200 OK', headers)
            return [response_data]

        else:
            response_body = {'error': 'Método não suportado.'}
            response_data = json.dumps(response_body, ensure_ascii=False).encode('utf-8')
            start_response('405 Method Not Allowed', headers)
            return [response_data]

    except Exception as e:
        print(f"Erro no servidor: {e}")
        response_body = {'error': 'Erro interno no servidor.', 'details': str(e)}
        response_data = json.dumps(response_body, ensure_ascii=False).encode('utf-8')
        start_response('500 Internal Server Error', [('Content-Type', 'application/json; charset=utf-8')])
        return [response_data]
