# CENTRO DE TREINAMENTO SÃO PAULO SKILLS

Sistema de Gestão de Treinamento para ocupaçÕes da **São Paulo Skills** - SENAI-SP

**Produção:** [https://seudominio.com.br/ctspskills](https://seudominio.com.br/ctspskills)

---

## Stack Tecnológica

### Backend
| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework | FastAPI |
| Banco de dados | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Autenticação | JWT (python-jose) + OAuth2 |
| Arquitetura | DDD (Domain-Driven Design) + Clean Architecture |

### Frontend
| Componente | Tecnologia |
|---|---|
| Framework | React 18 + TypeScript |
| Build tool | Vite |
| State management | Zustand |
| Estilização | Tailwind CSS |
| Forms | React Hook Form + Zod |
| HTTP Client | Axios |
| Editor de texto | TipTap (rich text) |
| Geração de PDF | jsPDF + jspdf-autotable |

---

## Funcionalidades

### Por Role

| Funcionalidade | Super Admin | Avaliador | Competidor |
|---|:---:|:---:|:---:|
| Dashboard com métricas gerais | ✅ | ✅ | ✅ |
| Gestão de usuários (ativar/desativar/excluir) | ✅ | — | — |
| Configurações da plataforma (logo, nome) | ✅ | — | — |
| Gestão de modalidades | ✅ | ✅ | — |
| Gestão de competidores | ✅ | ✅ | — |
| Registro e aprovação de treinamentos | ✅ | ✅ | ✅ |
| Editar / excluir treinamentos | ✅ | ✅ | — |
| Criação e gestão de avaliações (exames) | ✅ | ✅ | — |
| Lançamento de notas | ✅ | ✅ | — |
| Relatórios PDF — todos os competidores/modalidades | ✅ | — | — |
| Relatórios PDF — seus competidores/modalidades | ✅ | ✅ | — |
| Relatório Geral (visão plataforma) | ✅ | — | — |
| Visualizar próprias notas e treinamentos | ✅ | ✅ | ✅ |

### Tipos de Relatório PDF
- **Por Competidor** — treinamentos, horas, gráficos e notas de avaliações
- **Por Modalidade** — visão geral com todos os competidores, médias e horas
- **Presença** — frequência de treinos filtrada por tipo (SENAI / Externo / Ambos)
- **Ranking** — classificação por média de notas com gráfico
- **Horas de Treinamento** — detalhamento SENAI vs Externo por competidor
- **Relatório Geral** — panorama completo de todas as modalidades *(somente admin)*

---

## Estrutura do Projeto

```
ct-spskills-914/
├── src/                         # Backend FastAPI
│   ├── application/             # Casos de uso e DTOs
│   ├── config/                  # Configurações (Pydantic Settings)
│   ├── domain/                  # Entidades, repositórios e regras de negócio
│   ├── infrastructure/          # SQLAlchemy models e implementações
│   ├── presentation/            # Routers FastAPI e schemas Pydantic
│   └── shared/                  # Código compartilhado (base classes, utils)
├── frontend/                    # Frontend React
│   └── src/
│       ├── components/          # Componentes reutilizáveis e layout
│       ├── pages/               # Páginas por role (admin, evaluator, competitor)
│       ├── services/            # Serviços de API (axios)
│       ├── stores/              # Estado global (Zustand)
│       ├── types/               # Tipos TypeScript
│       └── utils/               # Utilitários (geração de PDF, etc.)
├── migrations/                  # Alembic migrations
│   └── versions/
├── scripts/                     # Scripts utilitários
├── alembic.ini
├── requirements.txt
├── pyproject.toml
├── .env.example
├── DEPLOY_DEBIAN12.md           # Tutorial completo de implantação
└── README.md
```

---

## Desenvolvimento Local

### Pré-requisitos
- Python 3.12+
- Node.js 18+
- PostgreSQL 15+

### Backend

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações locais

# Executar migrations
alembic upgrade head

# Iniciar servidor de desenvolvimento
uvicorn src.presentation.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

### Acessos Locais

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## Implantação no Servidor

> Para o tutorial completo passo a passo, consulte [DEPLOY_DEBIAN12.md](DEPLOY_DEBIAN12.md).

### Resumo rápido

```bash
# 1. No servidor — extrair projeto
mkdir -p /var/www/ctspskills
unzip /tmp/ctspskills.zip -d /var/www/ctspskills

# 2. PostgreSQL
su - postgres -c "psql"
# CREATE USER spskills WITH PASSWORD 'SENHA';
# CREATE DATABASE spskills_db OWNER spskills;
# \q

# 3. Backend
cd /var/www/ctspskills
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # editar com nano .env
alembic upgrade head

# 4. Frontend
cd frontend
npm install
npm run build
cp -r dist/* /var/www/ctspskills/public/

# 5. Serviço systemd, Apache, SSL → ver DEPLOY_DEBIAN12.md
```

### Arquivos para enviar ao servidor

| Incluir | Excluir |
|---|---|
| `src/` | `venv/` |
| `frontend/` (sem `dist/` e `node_modules/`) | `node_modules/` |
| `migrations/` | `frontend/dist/` |
| `scripts/` | `.git/` |
| `alembic.ini` | `__pycache__/` |
| `requirements.txt` | `uploads/` |
| `pyproject.toml` | `.env` |
| `.env.example` | `docker/`, `docker-compose*.yml` |

### Atualizar instalação existente

```bash
# No servidor
systemctl stop spskills

# Backup (opcional)
cp -r /var/www/ctspskills /var/www/ctspskills_backup_$(date +%Y%m%d)

# Substituir código
rm -rf /var/www/ctspskills/src /var/www/ctspskills/frontend /var/www/ctspskills/migrations
unzip /tmp/ctspskills.zip -d /var/www/ctspskills

# Backend
cd /var/www/ctspskills
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Frontend
cd frontend
npm install
npm run build
cp -r dist/* /var/www/ctspskills/public/

chown -R www-data:www-data /var/www/ctspskills
systemctl start spskills
systemctl status spskills
```

---

## Acessos de Produção

| Serviço | URL |
|---|---|
| Aplicação | https://seudominio.com.br/ctspskills |
| API | https://seudominio.com.br/api/v1 |
| Servidor | SEU_IP_DO_SERVIDOR |

---

## Principais Endpoints da API

### Autenticação
| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/auth/login` | Login (retorna tokens JWT) |
| POST | `/api/v1/auth/refresh` | Renovar access token |
| POST | `/api/v1/auth/logout` | Invalidar refresh token |

### Usuários
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/users/me` | Dados do usuário autenticado |
| GET | `/api/v1/users` | Listar usuários *(admin)* |
| PUT | `/api/v1/users/{id}/activate` | Ativar usuário *(admin)* |
| PUT | `/api/v1/users/{id}/deactivate` | Desativar usuário *(admin)* |
| DELETE | `/api/v1/users/{id}` | Excluir usuário *(admin)* |
| GET | `/api/v1/users/me/modalities` | Modalidades do avaliador autenticado |

### Modalidades
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/modalities` | Listar modalidades |
| POST | `/api/v1/modalities` | Criar modalidade |
| POST | `/api/v1/modalities/{id}/competitors` | Inscrever competidor |
| GET | `/api/v1/modalities/{id}/enrollments` | Listar inscrições |

### Competidores
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/competitors` | Listar competidores |
| GET | `/api/v1/competitors/by-modality/{id}` | Competidores por modalidade |

### Treinamentos
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/trainings` | Listar treinamentos |
| POST | `/api/v1/trainings` | Registrar treinamento |
| PUT | `/api/v1/trainings/{id}` | Atualizar treinamento |
| DELETE | `/api/v1/trainings/{id}` | Excluir treinamento |
| PUT | `/api/v1/trainings/{id}/approve` | Aprovar treinamento |
| GET | `/api/v1/trainings/statistics` | Estatísticas de treinamento |

### Avaliações (Exames)
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/exams` | Listar avaliações |
| POST | `/api/v1/exams` | Criar avaliação |
| POST | `/api/v1/exams/{id}/grades` | Lançar nota |

### Analytics
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/analytics/overview` | Visão geral da plataforma |
| GET | `/api/v1/analytics/training-hours` | Horas de treinamento |
| GET | `/api/v1/analytics/grades` | Dados de notas |

### Configurações da Plataforma
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/platform/settings` | Obter configurações |
| PUT | `/api/v1/platform/settings` | Atualizar configurações |
| POST | `/api/v1/platform/logo` | Upload de logo |

---

## Roles e Permissões

| Role | Descrição |
|---|---|
| `super_admin` | Acesso total — gerencia usuários, configurações e todos os dados |
| `evaluator` | Gerencia competidores e modalidades atribuídas, lança notas, gera relatórios dos seus competidores |
| `competitor` | Registra próprios treinamentos e visualiza seu desempenho |

---

## Regras de Negócio

| Código | Regra |
|---|---|
| RN02 | Avaliador deve estar atribuído à modalidade para lançar notas |
| RN03 | Nota deve estar entre 0 e `max_score` da competência |
| RN08 | Competência avaliada deve pertencer ao exame |
| RN12 | Access token expira em 15 min; refresh token em 7 dias |
| RN13 | Senha mínima: 8 chars, maiúscula, minúscula, número e caractere especial |
| RN15 | Rate limiting: 100 req/min por IP |

---

## Comandos Úteis

### Backend
```bash
# Criar nova migration
alembic revision --autogenerate -m "descricao"

# Executar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Histórico de migrations
alembic history
```

### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Build de produção
npm run build

# Verificar tipos TypeScript
npx tsc --noEmit

# Linting
npm run lint
```

### Servidor
```bash
# Gerenciar serviço
systemctl start|stop|restart|status spskills

# Logs em tempo real
journalctl -u spskills -f
tail -f /var/log/spskills/error.log

# Apache
apache2ctl configtest
systemctl reload apache2

# SSL
certbot renew --dry-run
```

---

## Licença

Projeto desenvolvido pelo Prof. Weverton Lubask para uso interno das Modalidades da São Paulo Skills.
