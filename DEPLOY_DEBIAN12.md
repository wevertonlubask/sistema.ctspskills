# Tutorial de Implantação — SPSkills no Debian 12

Guia completo para implantar o sistema SPSkills em um servidor Debian 12 (Bookworm) do zero.

**Domínio:** `seudominio.com.br`
**Servidor:** `SEU_IP_DO_SERVIDOR`
**Diretório do projeto:** `/var/www/ctspskills`
**Stack:** FastAPI (Python 3.12) + React 18 + PostgreSQL 15 + Apache2

---

## Índice

1. [Preparar e transferir os arquivos](#1-preparar-e-transferir-os-arquivos)
2. [Instalar dependências no servidor](#2-instalar-dependências-no-servidor)
3. [Configurar o PostgreSQL](#3-configurar-o-postgresql)
4. [Extrair o projeto no servidor](#4-extrair-o-projeto-no-servidor)
5. [Configurar o backend (FastAPI)](#5-configurar-o-backend-fastapi)
6. [Configurar o frontend (React)](#6-configurar-o-frontend-react)
7. [Configurar o serviço Systemd](#7-configurar-o-serviço-systemd)
8. [Configurar o Apache](#8-configurar-o-apache)
9. [Configurar HTTPS com Certbot](#9-configurar-https-com-certbot)
10. [Configurar o Firewall](#10-configurar-o-firewall)
11. [Primeiro acesso ao sistema](#11-primeiro-acesso-ao-sistema)
12. [Atualizar o sistema](#12-atualizar-o-sistema)
13. [Troubleshooting](#13-troubleshooting)
14. [Checklist final](#14-checklist-final)
15. [Referência rápida de comandos](#15-referência-rápida-de-comandos)

---

## 1. Preparar e Transferir os Arquivos

> Execute esta etapa no **seu computador local** (Windows).

### 1.1 O que enviar ao servidor

Envie apenas as pastas e arquivos abaixo. **Não envie** `venv/`, `node_modules/`, `frontend/dist/`, `.env` nem `.git/`.

```
ct-spskills-914/
├── src/                          ← Backend (obrigatório)
│   ├── application/
│   ├── config/
│   ├── domain/
│   ├── infrastructure/
│   ├── presentation/
│   └── shared/
├── frontend/                     ← Frontend (obrigatório)
│   ├── src/                      ← Código-fonte React
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js
│   └── postcss.config.js
│   (⚠ NÃO inclua: node_modules/ e dist/)
├── migrations/                   ← Migrações Alembic (obrigatório)
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── scripts/                      ← Scripts utilitários
├── alembic.ini                   ← Config Alembic (obrigatório)
├── requirements.txt              ← Dependências Python (obrigatório)
├── pyproject.toml
└── .env.example                  ← Modelo de variáveis de ambiente
```

### 1.2 Compactar os arquivos

**Opção A — 7-Zip (recomendado):**
1. Abra o 7-Zip e navegue até `D:\Projetos\ct-spskills-914`
2. Selecione: `src`, `frontend`, `migrations`, `scripts`, `alembic.ini`, `requirements.txt`, `pyproject.toml`, `.env.example`
3. Clique com o botão direito → **7-Zip → Adicionar ao arquivo** → salve como `ctspskills.zip`

> **Atenção:** Ao selecionar a pasta `frontend`, certifique-se de que `node_modules/` e `dist/` não estão incluídas. Se estiverem presentes, exclua-as explicitamente no 7-Zip.

**Opção B — PowerShell:**

```powershell
# Execute no PowerShell a partir da pasta do projeto
cd D:\Projetos\ct-spskills-914

Compress-Archive -Path `
  "src", `
  "migrations", `
  "scripts", `
  "alembic.ini", `
  "requirements.txt", `
  "pyproject.toml", `
  ".env.example" `
  -DestinationPath "..\ctspskills_backend.zip" -Force

# Frontend separado (sem node_modules e dist)
$frontendItems = Get-ChildItem frontend | Where-Object { $_.Name -notin @('node_modules','dist','.cache') }
Compress-Archive -Path ($frontendItems.FullName) -DestinationPath "..\ctspskills_frontend.zip" -Force
```

### 1.3 Transferir para o servidor

**Via SCP (PowerShell / terminal):**

```bash
scp ctspskills.zip root@SEU_IP_DO_SERVIDOR:/tmp/
```

**Via FileZilla:**
1. Conecte: Host `SEU_IP_DO_SERVIDOR`, Usuário `root`, Porta `22`
2. Faça upload do `.zip` para `/tmp/`

---

## 2. Instalar Dependências no Servidor

> A partir daqui, todos os comandos são executados no **servidor** via SSH.

```bash
ssh root@SEU_IP_DO_SERVIDOR
```

### 2.1 Atualizar o sistema

```bash
apt update && apt upgrade -y
apt install -y curl wget gnupg2 software-properties-common \
    build-essential libpq-dev unzip git
```

### 2.2 Instalar Python 3.12

O Debian 12 vem com Python 3.11. Para instalar o 3.12:

```bash
# Adicionar repositório deadsnakes
apt install -y python3.12 python3.12-venv python3.12-dev

# Verificar
python3.12 --version
```

> Se `python3.12` não estiver disponível nos repos padrão:
> ```bash
> add-apt-repository ppa:deadsnakes/ppa
> apt update
> apt install -y python3.12 python3.12-venv python3.12-dev
> ```

### 2.3 Instalar Node.js 20 LTS

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Verificar
node --version   # deve ser v20.x.x
npm --version
```

### 2.4 Instalar e verificar o PostgreSQL 15

```bash
# Verificar se já está instalado
psql --version

# Se não estiver instalado:
apt install -y postgresql postgresql-contrib
systemctl enable postgresql
systemctl start postgresql
```

### 2.5 Instalar e verificar o Apache2

```bash
apt install -y apache2

# Habilitar módulos necessários
a2enmod proxy proxy_http proxy_wstunnel rewrite headers ssl

systemctl enable apache2
systemctl restart apache2
```

### 2.6 Instalar o Certbot

```bash
apt install -y certbot python3-certbot-apache
```

---

## 3. Configurar o PostgreSQL

### 3.1 Criar usuário e banco de dados

```bash
su - postgres -c "psql"
```

No prompt do PostgreSQL:

```sql
-- Criar usuário (escolha uma senha segura)
CREATE USER spskills WITH PASSWORD 'SUA_SENHA_SEGURA_AQUI';

-- Criar banco de dados
CREATE DATABASE spskills_db OWNER spskills;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE spskills_db TO spskills;

-- Verificar
\l

-- Sair
\q
```

### 3.2 Testar a conexão

```bash
psql -U spskills -d spskills_db -h localhost -c "SELECT version();"
# Deve pedir a senha e retornar a versão do PostgreSQL
```

Se der erro de autenticação, edite `/etc/postgresql/15/main/pg_hba.conf`:

```bash
nano /etc/postgresql/15/main/pg_hba.conf
```

Verifique/adicione:

```
# TYPE  DATABASE        USER            ADDRESS         METHOD
host    spskills_db     spskills        127.0.0.1/32    md5
local   spskills_db     spskills                        md5
```

Reinicie o PostgreSQL:

```bash
systemctl restart postgresql
```

---

## 4. Extrair o Projeto no Servidor

```bash
# Criar diretório do projeto
mkdir -p /var/www/ctspskills

# Extrair o arquivo
unzip /tmp/ctspskills.zip -d /var/www/ctspskills

# Verificar a estrutura
ls -la /var/www/ctspskills
# Deve mostrar: src/  frontend/  migrations/  alembic.ini  requirements.txt  etc.
```

> **Atenção:** Se os arquivos ficaram dentro de uma subpasta (ex: `ct-spskills-914/`):
> ```bash
> mv /var/www/ctspskills/ct-spskills-914/* /var/www/ctspskills/
> rmdir /var/www/ctspskills/ct-spskills-914
> ```

```bash
# Remover arquivo temporário
rm /tmp/ctspskills.zip
```

**Estrutura esperada:**

```
/var/www/ctspskills/
├── src/
├── frontend/
├── migrations/
├── scripts/
├── alembic.ini
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## 5. Configurar o Backend (FastAPI)

### 5.1 Criar ambiente virtual Python 3.12

```bash
cd /var/www/ctspskills
python3.12 -m venv venv
source venv/bin/activate

# Verificar
python --version  # deve mostrar Python 3.12.x
```

### 5.2 Instalar dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.3 Criar o arquivo de variáveis de ambiente

```bash
nano /var/www/ctspskills/.env
```

Cole o conteúdo abaixo, substituindo os valores em MAIÚSCULAS:

```env
# Ambiente
ENVIRONMENT=production

# Banco de Dados
DATABASE_URL=postgresql+asyncpg://spskills:SUA_SENHA_SEGURA_AQUI@localhost:5432/spskills_db

# JWT — gere uma chave com: openssl rand -hex 32
SECRET_KEY=SUA_CHAVE_SECRETA_AQUI
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS — domínios permitidos (sem barra no final)
CORS_ORIGINS=https://seudominio.com.br,https://www.seudominio.com.br

# Upload de arquivos
UPLOAD_DIR=/var/www/ctspskills/uploads
MAX_UPLOAD_SIZE=5242880

# Primeiro usuário administrador (criado automaticamente na 1ª execução)
FIRST_ADMIN_EMAIL=admin@seudominio.com.br
FIRST_ADMIN_PASSWORD=SUA_SENHA_ADMIN_AQUI
FIRST_ADMIN_NAME=Administrador
```

> **Gerar SECRET_KEY segura:**
> ```bash
> openssl rand -hex 32
> ```

### 5.4 Criar diretórios necessários

```bash
mkdir -p /var/www/ctspskills/uploads/platform
mkdir -p /var/www/ctspskills/public
```

### 5.5 Executar as migrações do banco de dados

```bash
cd /var/www/ctspskills
source venv/bin/activate
alembic upgrade head
```

A saída deve mostrar as migrações sendo aplicadas sem erros.

### 5.6 Testar o backend (opcional)

```bash
cd /var/www/ctspskills
source venv/bin/activate
uvicorn src.presentation.main:app --host 0.0.0.0 --port 8000
```

Acesse `http://SEU_IP_DO_SERVIDOR:8000/docs` — deve exibir a documentação da API.
Encerre com `Ctrl+C` após verificar.

---

## 6. Configurar o Frontend (React)

### 6.1 Instalar dependências npm

```bash
cd /var/www/ctspskills/frontend
npm install
```

> Isso instala todas as dependências declaradas no `package.json`, incluindo `jspdf` e `jspdf-autotable` (geração de relatórios PDF).

### 6.2 Configurar variável de ambiente de produção

```bash
nano /var/www/ctspskills/frontend/.env.production
```

Conteúdo:

```env
VITE_API_URL=/api/v1
```

### 6.3 Gerar o build de produção

```bash
cd /var/www/ctspskills/frontend
npm run build
```

O build é gerado em `frontend/dist/`. Aguarde — pode levar alguns minutos.

### 6.4 Copiar build para o diretório público

```bash
cp -r /var/www/ctspskills/frontend/dist/* /var/www/ctspskills/public/
```

---

## 7. Configurar o Serviço Systemd

O Systemd garante que o backend inicie automaticamente e reinicie em caso de falha.

### 7.1 Criar o arquivo de serviço

```bash
nano /etc/systemd/system/spskills.service
```

Conteúdo:

```ini
[Unit]
Description=SPSkills FastAPI Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/ctspskills
Environment="PATH=/var/www/ctspskills/venv/bin"
EnvironmentFile=/var/www/ctspskills/.env
ExecStart=/var/www/ctspskills/venv/bin/uvicorn \
    src.presentation.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4
Restart=always
RestartSec=5

# Logs
StandardOutput=append:/var/log/spskills/access.log
StandardError=append:/var/log/spskills/error.log

[Install]
WantedBy=multi-user.target
```

### 7.2 Criar diretório de logs

```bash
mkdir -p /var/log/spskills
```

### 7.3 Ajustar permissões

```bash
chown -R www-data:www-data /var/www/ctspskills
chmod -R 755 /var/www/ctspskills
chmod 600 /var/www/ctspskills/.env          # .env só para www-data
chown www-data:www-data /var/log/spskills
```

### 7.4 Habilitar e iniciar o serviço

```bash
systemctl daemon-reload
systemctl enable spskills
systemctl start spskills

# Verificar status (deve mostrar "active (running)")
systemctl status spskills
```

---

## 8. Configurar o Apache

### 8.1 Criar o Virtual Host

```bash
nano /etc/apache2/sites-available/spskills.conf
```

Conteúdo:

```apache
<VirtualHost *:80>
    ServerName seudominio.com.br
    ServerAlias www.seudominio.com.br

    DocumentRoot /var/www/ctspskills/public

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/spskills_error.log
    CustomLog ${APACHE_LOG_DIR}/spskills_access.log combined

    # Proxy para a API (Backend FastAPI)
    ProxyPreserveHost On
    ProxyPass /api http://127.0.0.1:8000/api
    ProxyPassReverse /api http://127.0.0.1:8000/api

    # Proxy para uploads (servidos pelo backend)
    ProxyPass /uploads http://127.0.0.1:8000/uploads
    ProxyPassReverse /uploads http://127.0.0.1:8000/uploads

    # Arquivos estáticos do Frontend
    <Directory /var/www/ctspskills/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted

        # SPA — redirecionar rotas desconhecidas para index.html
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    # Headers de segurança
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</VirtualHost>
```

### 8.2 Habilitar o site

```bash
a2ensite spskills.conf
a2dissite 000-default.conf   # Desabilitar site padrão (opcional)

apache2ctl configtest         # Deve retornar "Syntax OK"
systemctl reload apache2
```

### 8.3 Testar (antes do SSL)

Acesse `http://seudominio.com.br` — a aplicação deve abrir.

---

## 9. Configurar HTTPS com Certbot

### 9.1 Obter o certificado SSL

```bash
certbot --apache -d seudominio.com.br -d www.seudominio.com.br
```

Responda às perguntas interativas. O Certbot irá:
- Obter o certificado Let's Encrypt
- Criar `/etc/apache2/sites-available/spskills-le-ssl.conf`
- Configurar redirecionamento automático HTTP → HTTPS

### 9.2 Verificar o Virtual Host SSL

```bash
nano /etc/apache2/sites-available/spskills-le-ssl.conf
```

Confirme que contém as configurações de proxy e rewrite. O arquivo deve ficar assim:

```apache
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName seudominio.com.br
    ServerAlias www.seudominio.com.br

    DocumentRoot /var/www/ctspskills/public

    # Certificado SSL (adicionado automaticamente pelo Certbot)
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/seudominio.com.br/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/seudominio.com.br/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/spskills_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/spskills_ssl_access.log combined

    # Proxy para a API (Backend FastAPI)
    ProxyPreserveHost On
    ProxyPass /api http://127.0.0.1:8000/api
    ProxyPassReverse /api http://127.0.0.1:8000/api

    # Proxy para uploads
    ProxyPass /uploads http://127.0.0.1:8000/uploads
    ProxyPassReverse /uploads http://127.0.0.1:8000/uploads

    # Arquivos estáticos do Frontend
    <Directory /var/www/ctspskills/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted

        # SPA — redirecionar rotas desconhecidas para index.html
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    # Headers de segurança
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</VirtualHost>
</IfModule>
```

Após editar:

```bash
apache2ctl configtest
systemctl reload apache2
```

### 9.3 Verificar renovação automática

```bash
certbot renew --dry-run
# Deve mostrar "Congratulations, all simulated renewals succeeded"
```

---

## 10. Configurar o Firewall

```bash
apt install -y ufw

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh        # Porta 22
ufw allow http       # Porta 80
ufw allow https      # Porta 443

ufw enable

# Verificar
ufw status verbose
```

> **Segurança extra:** Instale o `fail2ban` para proteção contra tentativas de força bruta:
> ```bash
> apt install -y fail2ban
> systemctl enable fail2ban
> systemctl start fail2ban
> ```

---

## 11. Primeiro Acesso ao Sistema

### 11.1 Criar o usuário administrador

O primeiro usuário admin é criado automaticamente na primeira execução do backend, com as credenciais definidas no `.env`:

```env
FIRST_ADMIN_EMAIL=admin@seudominio.com.br
FIRST_ADMIN_PASSWORD=SUA_SENHA_ADMIN_AQUI
```

Se o admin não foi criado automaticamente, execute:

```bash
cd /var/www/ctspskills
source venv/bin/activate
python scripts/create_admin.py   # se existir script
```

### 11.2 Acessar o sistema

1. Acesse `https://seudominio.com.br`
2. Faça login com as credenciais do admin
3. **Troque a senha imediatamente** após o primeiro login
4. Vá em **Configurações** → faça upload da logo e configure o nome da plataforma

### 11.3 Verificar funcionalidades principais

- [ ] Login e logout funcionam
- [ ] Dashboard carrega com dados
- [ ] Upload de logo em Configurações funciona
- [ ] Menu **Relatórios** aparece e gera PDFs
- [ ] Rotas diretas funcionam (ex: `https://seudominio.com.br/dashboard`)
- [ ] API responde em `https://seudominio.com.br/api/v1/health` (se existir)

---

## 12. Atualizar o Sistema

Use este procedimento para atualizar o sistema com uma nova versão.

### 12.1 No seu computador local

1. Compacte o projeto atualizado (mesmas regras da [seção 1](#1-preparar-e-transferir-os-arquivos))
2. Transfira para `/tmp/` do servidor via SCP ou FileZilla

### 12.2 No servidor

```bash
# 1. Parar o serviço
systemctl stop spskills

# 2. Backup da versão atual (recomendado)
cp -r /var/www/ctspskills /var/www/ctspskills_backup_$(date +%Y%m%d_%H%M)

# 3. Remover código antigo (preserva .env, venv, uploads, public)
rm -rf /var/www/ctspskills/src \
       /var/www/ctspskills/frontend \
       /var/www/ctspskills/migrations \
       /var/www/ctspskills/scripts

# 4. Extrair nova versão
unzip /tmp/ctspskills.zip -d /var/www/ctspskills
rm /tmp/ctspskills.zip

# 5. Atualizar dependências Python
cd /var/www/ctspskills
source venv/bin/activate
pip install -r requirements.txt

# 6. Executar novas migrações (se houver)
alembic upgrade head

# 7. Rebuild do frontend
cd frontend
npm install
npm run build
cp -r dist/* /var/www/ctspskills/public/

# 8. Ajustar permissões
chown -R www-data:www-data /var/www/ctspskills

# 9. Reiniciar o serviço
systemctl start spskills

# 10. Verificar status
systemctl status spskills
journalctl -u spskills -n 20

# 11. Após confirmar que tudo funciona, remover backup
# rm -rf /var/www/ctspskills_backup_*
```

---

## 13. Troubleshooting

### Erro 502 Bad Gateway

O backend não está rodando:

```bash
systemctl status spskills
journalctl -u spskills -n 50 --no-pager
```

Tente iniciar manualmente para ver o erro:

```bash
cd /var/www/ctspskills
source venv/bin/activate
uvicorn src.presentation.main:app --host 127.0.0.1 --port 8000
```

---

### Página em branco no frontend (SPA)

O `RewriteEngine` não está ativo:

```bash
a2enmod rewrite
systemctl restart apache2
```

Verifique se o `AllowOverride All` está configurado no `<Directory>` do Apache.

---

### API retorna erro de CORS

Verifique o `.env`:

```bash
cat /var/www/ctspskills/.env | grep CORS
# CORS_ORIGINS=https://seudominio.com.br
```

Deve conter o domínio exato sem barra no final. Após alterar, reinicie:

```bash
systemctl restart spskills
```

---

### Erro de permissão no upload de arquivos

```bash
chown -R www-data:www-data /var/www/ctspskills/uploads
chmod -R 755 /var/www/ctspskills/uploads
systemctl restart spskills
```

---

### Erro na migration do Alembic

```bash
cd /var/www/ctspskills
source venv/bin/activate
alembic history          # Ver histórico
alembic current          # Ver versão atual
alembic upgrade head     # Aplicar migrations pendentes
```

Se houver conflito:

```bash
alembic downgrade -1     # Reverter 1 migration
alembic upgrade head     # Reaplicar
```

---

### Backend não conecta ao PostgreSQL

```bash
# Testar conexão direta
psql -U spskills -d spskills_db -h localhost

# Verificar se o PostgreSQL está rodando
systemctl status postgresql

# Ver logs do PostgreSQL
journalctl -u postgresql -n 30
```

---

### Certificado SSL expirado

```bash
certbot renew
systemctl reload apache2
```

---

### Ver logs em tempo real

```bash
# Backend
journalctl -u spskills -f

# Apache (erros)
tail -f /var/log/apache2/spskills_ssl_error.log

# Backend (arquivo de log)
tail -f /var/log/spskills/error.log
```

---

## 14. Checklist Final

### Infraestrutura
- [ ] Python 3.12 instalado (`python3.12 --version`)
- [ ] Node.js 20 instalado (`node --version`)
- [ ] PostgreSQL 15+ instalado e rodando
- [ ] Apache2 instalado com módulos: `proxy`, `proxy_http`, `rewrite`, `headers`, `ssl`
- [ ] Certbot instalado
- [ ] Firewall configurado (portas 22, 80, 443 abertas)

### Banco de Dados
- [ ] Usuário `spskills` criado com senha segura
- [ ] Banco `spskills_db` criado
- [ ] Conexão testada com sucesso (`psql -U spskills -d spskills_db -h localhost`)
- [ ] Migrações executadas (`alembic upgrade head`)

### Backend
- [ ] Ambiente virtual Python 3.12 criado (`venv/`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado com `DATABASE_URL`, `SECRET_KEY` e `CORS_ORIGINS`
- [ ] Diretório `uploads/platform/` criado
- [ ] Serviço `spskills` criado, habilitado e rodando (`active`)

### Frontend
- [ ] `npm install` executado (inclui `jspdf`, `jspdf-autotable`)
- [ ] `npm run build` executado com sucesso
- [ ] Arquivos copiados para `/var/www/ctspskills/public/`
- [ ] Permissões ajustadas (`chown -R www-data:www-data`)

### Apache e SSL
- [ ] Virtual Host `spskills.conf` criado e habilitado
- [ ] Certificado SSL obtido via Certbot
- [ ] `spskills-le-ssl.conf` contém configurações de proxy e rewrite
- [ ] `apache2ctl configtest` retorna `Syntax OK`
- [ ] HTTPS funcionando em `https://seudominio.com.br`

### Funcionalidades
- [ ] Login do admin funcionando
- [ ] Dashboard carrega corretamente
- [ ] Upload de logo em Configurações funciona
- [ ] Menu **Relatórios** aparece para admin e avaliadores
- [ ] Relatórios PDF sendo gerados corretamente
- [ ] Avaliadores veem apenas suas modalidades
- [ ] Todas as rotas da SPA funcionam (ex: acesso direto a `/dashboard`)
- [ ] Senha do admin alterada após o primeiro acesso

---

## 15. Referência Rápida de Comandos

```bash
# ===== SERVIÇO BACKEND =====
systemctl start spskills          # Iniciar
systemctl stop spskills           # Parar
systemctl restart spskills        # Reiniciar
systemctl status spskills         # Ver status
journalctl -u spskills -f         # Logs em tempo real
journalctl -u spskills -n 50      # Últimas 50 linhas de log

# ===== APACHE =====
apache2ctl configtest             # Verificar sintaxe da configuração
systemctl reload apache2          # Recarregar config (sem derrubar)
systemctl restart apache2         # Reiniciar completamente

# ===== BANCO DE DADOS =====
su - postgres -c "psql -d spskills_db"          # Conectar ao banco
psql -U spskills -d spskills_db -h localhost    # Conectar como spskills

# ===== MIGRAÇÕES =====
cd /var/www/ctspskills && source venv/bin/activate
alembic upgrade head              # Aplicar todas as migrações
alembic current                   # Ver versão atual
alembic history                   # Ver histórico

# ===== FRONTEND (rebuild) =====
cd /var/www/ctspskills/frontend
npm install && npm run build
cp -r dist/* /var/www/ctspskills/public/
chown -R www-data:www-data /var/www/ctspskills/public

# ===== SSL =====
certbot renew --dry-run           # Testar renovação
certbot renew                     # Renovar manualmente

# ===== LOGS =====
tail -f /var/log/spskills/error.log
tail -f /var/log/apache2/spskills_ssl_error.log
tail -f /var/log/apache2/spskills_error.log

# ===== PERMISSÕES (corrigir) =====
chown -R www-data:www-data /var/www/ctspskills
chmod 600 /var/www/ctspskills/.env
```

---

**Pronto!** O sistema SPSkills está implantado e acessível em `https://seudominio.com.br`
