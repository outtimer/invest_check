# Imagem base com Node.js
FROM node:20-slim

# Instala Python e pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /usr/src/app

# Copia arquivos de package para instalar dependências primeiro
COPY package*.json ./

# Instala dependências Node
RUN npm install

# Copia o restante do projeto
COPY . .

# Instala dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD ["node", "src/backend/server.js"]
