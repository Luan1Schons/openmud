# Dockerfile para OpenMud MUD Server
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto
COPY . .

# Expõe a porta (será sobrescrita pela variável PORT do Railway)
EXPOSE 4000

# Comando para iniciar o servidor
CMD ["python3", "server.py"]

