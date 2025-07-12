import requests
import json
import re
from bs4 import BeautifulSoup
import time

def get_instagram_posts(username):
    """
    Busca as últimas publicações do Instagram usando web scraping
    """
    url = f"https://www.instagram.com/{username}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procura por scripts que contêm dados do Instagram
        scripts = soup.find_all('script', type='application/ld+json')
        
        posts = []
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'mainEntityofPage' in data:
                    # Extrai informações das publicações
                    if 'image' in data:
                        posts.append({
                            'image': data['image'],
                            'caption': data.get('description', ''),
                            'timestamp': data.get('datePublished', '')
                        })
            except json.JSONDecodeError:
                continue
        
        # Se não encontrou dados estruturados, tenta extrair de outras formas
        if not posts:
            # Procura por imagens e textos
            images = soup.find_all('img')
            for img in images[:6]:  # Primeiras 6 imagens
                if img.get('src') and 'instagram' in img.get('src', ''):
                    posts.append({
                        'image': img['src'],
                        'caption': img.get('alt', ''),
                        'timestamp': ''
                    })
        
        return posts[:6]  # Retorna no máximo 6 posts
        
    except Exception as e:
        print(f"Erro ao buscar posts: {e}")
        return []

def update_html_with_real_posts(posts):
    """
    Atualiza o HTML com as publicações reais do Instagram
    """
    if not posts:
        print("Nenhuma publicação encontrada")
        return
    
    # Lê o arquivo HTML atual
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Cria o HTML das publicações
    posts_html = ""
    for i, post in enumerate(posts):
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
                        "{post['caption'][:100]}{'...' if len(post['caption']) > 100 else ''}"
                    </div>
                    <div class="post-time">há {i+1} {'dia' if i+1 == 1 else 'dias'}</div>
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
    
    print(f"HTML atualizado com {len(posts)} publicações reais!")

if __name__ == "__main__":
    username = "decolonializando.filos"
    print(f"Buscando publicações do @{username}...")
    
    posts = get_instagram_posts(username)
    
    if posts:
        print(f"Encontradas {len(posts)} publicações")
        update_html_with_real_posts(posts)
    else:
        print("Nenhuma publicação encontrada. Usando conteúdo padrão.") 