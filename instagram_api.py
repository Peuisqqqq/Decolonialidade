import requests
import json
import time

def get_instagram_posts_api(username):
    """
    Busca as últimas publicações do Instagram usando a API pública
    """
    # URL da API pública do Instagram
    url = f"https://www.instagram.com/{username}/?__a=1&__d=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Referer': f'https://www.instagram.com/{username}/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        posts = []
        
        # Tenta diferentes estruturas de dados que o Instagram pode retornar
        if 'graphql' in data and 'user' in data['graphql']:
            user_data = data['graphql']['user']
            edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
            
            for edge in edges[:6]:  # Primeiras 6 publicações
                node = edge['node']
                
                # Pega a URL da imagem
                if 'display_url' in node:
                    image_url = node['display_url']
                elif 'thumbnail_src' in node:
                    image_url = node['thumbnail_src']
                else:
                    continue
                
                # Pega a legenda
                caption = ""
                if 'edge_media_to_caption' in node and node['edge_media_to_caption']['edges']:
                    caption = node['edge_media_to_caption']['edges'][0]['node']['text']
                
                posts.append({
                    'image': image_url,
                    'caption': caption,
                    'timestamp': node.get('taken_at_timestamp', '')
                })
        
        return posts
        
    except Exception as e:
        print(f"Erro ao buscar posts via API: {e}")
        return []

def create_fallback_posts():
    """
    Cria posts de fallback baseados no conteúdo do site
    """
    return [
        {
            'image': 'src/FILHO DA PUTA.png',
            'caption': 'A colonialidade não acabou, ela se modernizou. Resistir é existir! ✊🏾 #Decolonialidade #Resistência #FilosofiaUFPE',
            'timestamp': ''
        },
        {
            'image': 'src/Sônia Guajajara.jpeg',
            'caption': 'Sônia Guajajara: uma voz que ecoa pela defesa dos povos indígenas. Sua luta é nossa luta! 🌿 #Indígenas #DireitosTerra #SôniaGuajajara',
            'timestamp': ''
        },
        {
            'image': 'src/Silvio de Almeida.jpg',
            'caption': 'Silvio de Almeida nos ensina sobre racismo estrutural. Conhecimento é poder! 📚 #RacismoEstrutural #SilvioDeAlmeida #Filosofia',
            'timestamp': ''
        },
        {
            'image': 'src/Marielle Franco.jpeg',
            'caption': 'Marielle Franco presente! Sua luta continua viva em cada um de nós. ✊🏾 #MariellePresente #DireitosHumanos #Resistência',
            'timestamp': ''
        },
        {
            'image': 'src/Ailton Krenak.webp',
            'caption': 'Ailton Krenak: sabedoria ancestral em tempos de crise. A terra não é mercadoria! 🌿 #AiltonKrenak #SabedoriaIndígena #Terra',
            'timestamp': ''
        },
        {
            'image': 'src/Lélia Gonzalez.jpg',
            'caption': 'Lélia Gonzalez: intelectual negra que revolucionou o pensamento brasileiro. Sua obra é fundamental! 📚 #LéliaGonzalez #FeminismoNegro #Intelectual',
            'timestamp': ''
        }
    ]

def update_html_with_posts(posts):
    """
    Atualiza o HTML com as publicações do Instagram
    """
    if not posts:
        print("Nenhuma publicação encontrada, usando posts de fallback")
        posts = create_fallback_posts()
    
    # Lê o arquivo HTML atual
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Cria o HTML das publicações
    posts_html = ""
    for i, post in enumerate(posts):
        # Determina o tempo baseado no índice
        if i == 0:
            time_text = "há 2 horas"
        elif i == 1:
            time_text = "há 5 horas"
        elif i == 2:
            time_text = "há 1 dia"
        elif i == 3:
            time_text = "há 2 dias"
        elif i == 4:
            time_text = "há 3 dias"
        else:
            time_text = "há 1 semana"
        
        posts_html += f'''
                <div class="instagram-post">
                    <div class="post-header">
                        <img src="src/Marielle Franco.jpeg" alt="Perfil" class="profile-pic">
                        <div class="post-info">
                            <strong>decolonializando.filos</strong>
                            <span class="post-location">Recife, Brasil</span>
                        </div>
                    </div>
                    <div class="post-image">
                        <img src="{post['image']}" alt="Post do Instagram" onerror="this.src='src/FILHO DA PUTA.png'">
                    </div>
                    <div class="post-actions">
                        <button class="action-btn">❤️</button>
                        <button class="action-btn">💬</button>
                        <button class="action-btn">📤</button>
                    </div>
                    <div class="post-caption">
                        <strong>decolonializando.filos</strong> 
                        "{post['caption']}"
                    </div>
                    <div class="post-time">{time_text}</div>
                </div>
        '''
    
    # Substitui o conteúdo do feed do Instagram
    start_marker = '            <div class="instagram-feed">'
    end_marker = '            </div>'
    
    start_pos = html_content.find(start_marker)
    end_pos = html_content.find(end_marker, start_pos) + len(end_marker)
    
    new_content = start_marker + '\n' + posts_html + '\n            ' + end_marker
    
    updated_html = html_content[:start_pos] + new_content + html_content[end_pos:]
    
    # Salva o arquivo atualizado
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"HTML atualizado com {len(posts)} publicações!")

if __name__ == "__main__":
    username = "decolonializando.filos"
    print(f"Buscando publicações do @{username}...")
    
    # Tenta primeiro com a API
    posts = get_instagram_posts_api(username)
    
    if not posts:
        print("API não funcionou, usando posts de fallback...")
        posts = create_fallback_posts()
    
    update_html_with_posts(posts) 