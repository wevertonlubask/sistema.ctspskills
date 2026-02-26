"""
Script para popular o banco de dados com dados de teste.

Uso:
    cd ct-spskills-914
    python -m scripts.seed_database

    Ou com variável de ambiente:
    DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname python -m scripts.seed_database

Credenciais de teste:
    Admin:      admin@spskills.com / Admin123!
    Avaliador:  avaliador@spskills.com / Avaliador123!
    Competidor: competidor@spskills.com / Competidor123!
"""

import asyncio
import os
import random
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Tenta importar settings do projeto, fallback para variável de ambiente
try:
    from src.config.settings import get_settings

    settings = get_settings()
    DATABASE_URL = settings.database_url
except ImportError:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/ct_spskills"
    )


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


# ============== DADOS DE TESTE ==============

# Usuários de teste
USERS = [
    {
        "id": str(uuid4()),
        "email": "admin@spskills.com",
        "password": "Admin123!",
        "full_name": "Administrador Sistema",
        "role": "super_admin",
        "status": "active",
    },
    {
        "id": str(uuid4()),
        "email": "avaliador@spskills.com",
        "password": "Avaliador123!",
        "full_name": "Carlos Silva",
        "role": "evaluator",
        "status": "active",
    },
    {
        "id": str(uuid4()),
        "email": "avaliador2@spskills.com",
        "password": "Avaliador123!",
        "full_name": "Ana Oliveira",
        "role": "evaluator",
        "status": "active",
    },
    {
        "id": str(uuid4()),
        "email": "competidor@spskills.com",
        "password": "Competidor123!",
        "full_name": "João Santos",
        "role": "competitor",
        "status": "active",
    },
    {
        "id": str(uuid4()),
        "email": "competidor2@spskills.com",
        "password": "Competidor123!",
        "full_name": "Maria Souza",
        "role": "competitor",
        "status": "active",
    },
    {
        "id": str(uuid4()),
        "email": "competidor3@spskills.com",
        "password": "Competidor123!",
        "full_name": "Pedro Lima",
        "role": "competitor",
        "status": "active",
    },
    {
        "id": str(uuid4()),
        "email": "competidor4@spskills.com",
        "password": "Competidor123!",
        "full_name": "Ana Clara Ferreira",
        "role": "competitor",
        "status": "active",
    },
    {
        "id": str(uuid4()),
        "email": "competidor5@spskills.com",
        "password": "Competidor123!",
        "full_name": "Lucas Mendes",
        "role": "competitor",
        "status": "active",
    },
]

# Modalidades WorldSkills
MODALITIES = [
    {
        "id": str(uuid4()),
        "code": "SOLD",
        "name": "Soldagem",
        "description": "Técnicas avançadas de soldagem TIG, MIG/MAG e eletrodo revestido",
        "is_active": True,
        "min_training_hours": 500,
    },
    {
        "id": str(uuid4()),
        "code": "USIN",
        "name": "Tornearia CNC",
        "description": "Usinagem em tornos CNC e convencionais",
        "is_active": True,
        "min_training_hours": 450,
    },
    {
        "id": str(uuid4()),
        "code": "CAD",
        "name": "Desenho Mecânico CAD",
        "description": "Projeto e desenho técnico utilizando softwares CAD",
        "is_active": True,
        "min_training_hours": 400,
    },
    {
        "id": str(uuid4()),
        "code": "ELET",
        "name": "Instalações Elétricas",
        "description": "Instalações elétricas prediais e industriais",
        "is_active": True,
        "min_training_hours": 480,
    },
    {
        "id": str(uuid4()),
        "code": "MECA",
        "name": "Mecatrônica",
        "description": "Integração de sistemas mecânicos, eletrônicos e de automação",
        "is_active": True,
        "min_training_hours": 550,
    },
]

# Competências por modalidade
COMPETENCES = {
    "SOLD": [
        {
            "name": "Soldagem TIG",
            "description": "Técnicas de soldagem TIG em diversos materiais",
            "weight": 1.5,
            "max_score": 100,
        },
        {
            "name": "Soldagem MIG/MAG",
            "description": "Processos de soldagem MIG e MAG",
            "weight": 1.5,
            "max_score": 100,
        },
        {
            "name": "Leitura de Desenho",
            "description": "Interpretação de desenhos técnicos de soldagem",
            "weight": 1.0,
            "max_score": 100,
        },
        {
            "name": "Segurança do Trabalho",
            "description": "Normas e práticas de segurança em soldagem",
            "weight": 0.5,
            "max_score": 100,
        },
        {
            "name": "Qualidade de Acabamento",
            "description": "Avaliação visual e dimensional da solda",
            "weight": 1.5,
            "max_score": 100,
        },
    ],
    "USIN": [
        {
            "name": "Programação CNC",
            "description": "Programação de tornos CNC",
            "weight": 2.0,
            "max_score": 100,
        },
        {
            "name": "Metrologia",
            "description": "Medição e controle dimensional",
            "weight": 1.0,
            "max_score": 100,
        },
        {
            "name": "Setup de Máquina",
            "description": "Preparação e ajuste de máquinas",
            "weight": 1.0,
            "max_score": 100,
        },
        {
            "name": "Acabamento Superficial",
            "description": "Qualidade do acabamento das peças",
            "weight": 1.5,
            "max_score": 100,
        },
    ],
    "CAD": [
        {
            "name": "Modelagem 3D",
            "description": "Criação de modelos 3D paramétricos",
            "weight": 2.0,
            "max_score": 100,
        },
        {
            "name": "Detalhamento Técnico",
            "description": "Criação de desenhos técnicos detalhados",
            "weight": 1.5,
            "max_score": 100,
        },
        {
            "name": "Montagem",
            "description": "Montagem de conjuntos mecânicos",
            "weight": 1.0,
            "max_score": 100,
        },
        {
            "name": "Normas Técnicas",
            "description": "Aplicação de normas ABNT e ISO",
            "weight": 1.0,
            "max_score": 100,
        },
    ],
    "ELET": [
        {
            "name": "Instalação Residencial",
            "description": "Instalações elétricas residenciais",
            "weight": 1.5,
            "max_score": 100,
        },
        {
            "name": "Instalação Industrial",
            "description": "Instalações elétricas industriais",
            "weight": 1.5,
            "max_score": 100,
        },
        {
            "name": "Comandos Elétricos",
            "description": "Montagem de painéis e comandos",
            "weight": 1.5,
            "max_score": 100,
        },
        {
            "name": "NR-10",
            "description": "Segurança em instalações elétricas",
            "weight": 1.0,
            "max_score": 100,
        },
    ],
    "MECA": [
        {
            "name": "Pneumática",
            "description": "Sistemas pneumáticos industriais",
            "weight": 1.0,
            "max_score": 100,
        },
        {
            "name": "Hidráulica",
            "description": "Sistemas hidráulicos",
            "weight": 1.0,
            "max_score": 100,
        },
        {"name": "CLP", "description": "Programação de CLPs", "weight": 2.0, "max_score": 100},
        {
            "name": "Robótica",
            "description": "Programação de robôs industriais",
            "weight": 1.5,
            "max_score": 100,
        },
        {
            "name": "Integração de Sistemas",
            "description": "Integração de subsistemas mecatrônicos",
            "weight": 1.5,
            "max_score": 100,
        },
    ],
}

# Tipos de avaliação (valores do enum AssessmentType do backend)
ASSESSMENT_TYPES = ["simulation", "practical", "theoretical", "mixed"]

# Tipos de treinamento configuráveis
TRAINING_TYPE_CONFIGS = [
    {
        "code": "senai",
        "name": "SENAI",
        "description": "Treinamento realizado nas dependências do SENAI",
        "is_active": True,
        "display_order": 1,
    },
    {
        "code": "external",
        "name": "FORA",
        "description": "Treinamento realizado fora do SENAI (empresa, autônomo, etc)",
        "is_active": True,
        "display_order": 2,
    },
]


async def clear_tables(session: AsyncSession):
    """Limpar todas as tabelas em ordem de dependência."""
    tables = [
        "grade_audit_logs",
        "grades",
        "exam_competences",
        "exams",
        "training_sessions",
        "evidences",
        "enrollments",
        "competences",
        "competitors",
        "modalities",
        "training_type_configs",
        "refresh_tokens",
        "users",
    ]

    for table in tables:
        try:
            await session.execute(text(f"DELETE FROM {table}"))
        except Exception as e:
            print(f"Aviso: Tabela {table} não existe ou erro: {e}")

    await session.commit()
    print("✓ Tabelas limpas")


async def seed_users(session: AsyncSession) -> dict:
    """Criar usuários de teste."""
    user_ids = {}
    now = utc_now()

    for user in USERS:
        hashed = hash_password(user["password"])
        user_ids[user["email"]] = user["id"]

        await session.execute(
            text(
                """
                INSERT INTO users (id, email, password_hash, full_name, role, status, created_at, updated_at)
                VALUES (:id, :email, :password_hash, :full_name, :role, :status, :created_at, :updated_at)
            """
            ),
            {
                "id": user["id"],
                "email": user["email"],
                "password_hash": hashed,
                "full_name": user["full_name"],
                "role": user["role"],
                "status": user["status"],
                "created_at": now,
                "updated_at": now,
            },
        )

    await session.commit()
    print(f"✓ {len(USERS)} usuários criados")
    return user_ids


async def seed_training_type_configs(session: AsyncSession):
    """Criar configurações de tipos de treinamento."""
    now = utc_now()

    for config in TRAINING_TYPE_CONFIGS:
        await session.execute(
            text(
                """
                INSERT INTO training_type_configs (id, code, name, description, is_active, display_order, created_at, updated_at)
                VALUES (:id, :code, :name, :description, :is_active, :display_order, :created_at, :updated_at)
            """
            ),
            {
                "id": str(uuid4()),
                "code": config["code"],
                "name": config["name"],
                "description": config["description"],
                "is_active": config["is_active"],
                "display_order": config["display_order"],
                "created_at": now,
                "updated_at": now,
            },
        )

    await session.commit()
    print(f"✓ {len(TRAINING_TYPE_CONFIGS)} tipos de treinamento criados")


async def seed_modalities(session: AsyncSession) -> dict:
    """Criar modalidades."""
    modality_ids = {}
    now = utc_now()

    for modality in MODALITIES:
        modality_ids[modality["code"]] = modality["id"]

        await session.execute(
            text(
                """
                INSERT INTO modalities (id, code, name, description, is_active, min_training_hours, created_at, updated_at)
                VALUES (:id, :code, :name, :description, :is_active, :min_training_hours, :created_at, :updated_at)
            """
            ),
            {
                "id": modality["id"],
                "code": modality["code"],
                "name": modality["name"],
                "description": modality["description"],
                "is_active": modality["is_active"],
                "min_training_hours": modality["min_training_hours"],
                "created_at": now,
                "updated_at": now,
            },
        )

    await session.commit()
    print(f"✓ {len(MODALITIES)} modalidades criadas")
    return modality_ids


async def seed_competences(session: AsyncSession, modality_ids: dict) -> dict:
    """Criar competências para cada modalidade."""
    competence_ids = {}
    now = utc_now()
    count = 0

    for modality_code, competences in COMPETENCES.items():
        modality_id = modality_ids.get(modality_code)
        if not modality_id:
            continue

        competence_ids[modality_code] = []

        for comp in competences:
            comp_id = str(uuid4())
            competence_ids[modality_code].append(comp_id)

            await session.execute(
                text(
                    """
                    INSERT INTO competences (id, modality_id, name, description, weight, max_score, is_active, created_at, updated_at)
                    VALUES (:id, :modality_id, :name, :description, :weight, :max_score, :is_active, :created_at, :updated_at)
                """
                ),
                {
                    "id": comp_id,
                    "modality_id": modality_id,
                    "name": comp["name"],
                    "description": comp["description"],
                    "weight": comp["weight"],
                    "max_score": comp["max_score"],
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            count += 1

    await session.commit()
    print(f"✓ {count} competências criadas")
    return competence_ids


async def seed_competitors(session: AsyncSession, user_ids: dict) -> dict:
    """Criar perfis de competidores."""
    competitor_ids = {}
    now = utc_now()

    competitor_users = [u for u in USERS if u["role"] == "competitor"]

    for user in competitor_users:
        comp_id = str(uuid4())
        competitor_ids[user["email"]] = comp_id

        # Gera data de nascimento aleatória (18-25 anos)
        birth_year = random.randint(1999, 2006)
        birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))

        await session.execute(
            text(
                """
                INSERT INTO competitors (id, user_id, full_name, birth_date, document_number, phone, is_active, created_at, updated_at)
                VALUES (:id, :user_id, :full_name, :birth_date, :document_number, :phone, :is_active, :created_at, :updated_at)
            """
            ),
            {
                "id": comp_id,
                "user_id": user_ids[user["email"]],
                "full_name": user["full_name"],
                "birth_date": birth_date,
                "document_number": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                "phone": f"({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        )

    await session.commit()
    print(f"✓ {len(competitor_ids)} competidores criados")
    return competitor_ids


async def seed_enrollments(
    session: AsyncSession, competitor_ids: dict, modality_ids: dict, user_ids: dict
) -> dict:
    """Criar matrículas de competidores em modalidades."""
    enrollment_ids = {}
    now = utc_now()

    evaluator_id = user_ids.get("avaliador@spskills.com")
    evaluator2_id = user_ids.get("avaliador2@spskills.com")

    # Distribuir competidores entre modalidades
    competitor_list = list(competitor_ids.items())
    modality_list = list(modality_ids.items())

    # Contador por modalidade para alternar avaliadores
    modality_counters = {code: 0 for code, _ in modality_list}

    for _, (comp_email, comp_id) in enumerate(competitor_list):
        # Cada competidor em 1-2 modalidades
        num_modalities = random.randint(1, 2)
        selected_modalities = random.sample(modality_list, num_modalities)

        for modality_code, modality_id in selected_modalities:
            enrollment_id = str(uuid4())
            key = f"{comp_email}_{modality_code}"
            enrollment_ids[key] = enrollment_id

            # Alternar avaliadores POR MODALIDADE para garantir que cada avaliador
            # tenha matrículas em cada modalidade
            modality_counters[modality_code] += 1
            eval_id = evaluator_id if modality_counters[modality_code] % 2 == 1 else evaluator2_id

            enrolled_date = date.today() - timedelta(days=random.randint(30, 180))

            await session.execute(
                text(
                    """
                    INSERT INTO enrollments (id, competitor_id, modality_id, evaluator_id, enrolled_at, status, created_at, updated_at)
                    VALUES (:id, :competitor_id, :modality_id, :evaluator_id, :enrolled_at, :status, :created_at, :updated_at)
                """
                ),
                {
                    "id": enrollment_id,
                    "competitor_id": comp_id,
                    "modality_id": modality_id,
                    "evaluator_id": eval_id,
                    "enrolled_at": enrolled_date,
                    "status": "active",
                    "created_at": now,
                    "updated_at": now,
                },
            )

    await session.commit()
    print(f"✓ {len(enrollment_ids)} matrículas criadas")
    return enrollment_ids


async def seed_exams(
    session: AsyncSession, modality_ids: dict, competence_ids: dict, user_ids: dict
) -> dict:
    """Criar exames e avaliações."""
    exam_ids = {}
    now = utc_now()

    evaluator_id = user_ids.get("avaliador@spskills.com")

    exam_templates = [
        {"name": "Simulado Regional 2024", "type": "simulation", "days_ago": 60},
        {"name": "Avaliação Prática - Módulo 1", "type": "practical", "days_ago": 45},
        {"name": "Prova Teórica - Fundamentos", "type": "theoretical", "days_ago": 30},
        {"name": "Simulado Nacional 2024", "type": "simulation", "days_ago": 15},
        {"name": "Avaliação Mista - Final", "type": "mixed", "days_ago": 7},
    ]

    for modality_code, modality_id in modality_ids.items():
        exam_ids[modality_code] = []

        for template in exam_templates:
            exam_id = str(uuid4())
            exam_ids[modality_code].append(exam_id)

            exam_date = date.today() - timedelta(days=template["days_ago"])

            await session.execute(
                text(
                    """
                    INSERT INTO exams (id, name, description, modality_id, assessment_type, exam_date, is_active, created_by, created_at, updated_at)
                    VALUES (:id, :name, :description, :modality_id, :assessment_type, :exam_date, :is_active, :created_by, :created_at, :updated_at)
                """
                ),
                {
                    "id": exam_id,
                    "name": f"{template['name']} - {modality_code}",
                    "description": f"Avaliação de {template['type']} para modalidade {modality_code}",
                    "modality_id": modality_id,
                    "assessment_type": template["type"],
                    "exam_date": exam_date,
                    "is_active": True,
                    "created_by": evaluator_id,
                    "created_at": now,
                    "updated_at": now,
                },
            )

            # Vincular competências ao exame
            if modality_code in competence_ids:
                for comp_id in competence_ids[modality_code]:
                    await session.execute(
                        text(
                            """
                            INSERT INTO exam_competences (exam_id, competence_id)
                            VALUES (:exam_id, :competence_id)
                        """
                        ),
                        {"exam_id": exam_id, "competence_id": comp_id},
                    )

    await session.commit()
    total_exams = sum(len(exams) for exams in exam_ids.values())
    print(f"✓ {total_exams} exames criados")
    return exam_ids


async def seed_grades(
    session: AsyncSession,
    exam_ids: dict,
    competitor_ids: dict,
    competence_ids: dict,
    modality_ids: dict,
    enrollment_ids: dict,
    user_ids: dict,
):
    """Criar notas para os competidores."""
    now = utc_now()
    evaluator_id = user_ids.get("avaliador@spskills.com")
    grade_count = 0

    # Para cada competidor matriculado em uma modalidade
    for enrollment_key, _ in enrollment_ids.items():
        comp_email, modality_code = enrollment_key.rsplit("_", 1)
        competitor_id = competitor_ids.get(comp_email)

        if not competitor_id or modality_code not in exam_ids:
            continue

        # Para cada exame da modalidade
        for exam_id in exam_ids[modality_code]:
            # Para cada competência
            if modality_code not in competence_ids:
                continue

            for competence_id in competence_ids[modality_code]:
                # Gerar nota realista (60-100 com distribuição normal)
                score = min(100, max(0, random.gauss(78, 12)))
                score = round(score, 1)

                grade_id = str(uuid4())

                notes_options = [
                    "Bom desempenho",
                    "Precisa melhorar acabamento",
                    "Excelente execução",
                    "Atenção aos detalhes",
                    "Dentro do esperado",
                    None,
                ]

                await session.execute(
                    text(
                        """
                        INSERT INTO grades (id, exam_id, competitor_id, competence_id, score, notes, created_by, updated_by, created_at, updated_at)
                        VALUES (:id, :exam_id, :competitor_id, :competence_id, :score, :notes, :created_by, :updated_by, :created_at, :updated_at)
                    """
                    ),
                    {
                        "id": grade_id,
                        "exam_id": exam_id,
                        "competitor_id": competitor_id,
                        "competence_id": competence_id,
                        "score": score,
                        "notes": random.choice(notes_options),
                        "created_by": evaluator_id,
                        "updated_by": evaluator_id,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
                grade_count += 1

    await session.commit()
    print(f"✓ {grade_count} notas criadas")


async def seed_training_sessions(
    session: AsyncSession,
    competitor_ids: dict,
    modality_ids: dict,
    enrollment_ids: dict,
    user_ids: dict,
):
    """Criar sessões de treinamento."""
    now = utc_now()
    evaluator_id = user_ids.get("avaliador@spskills.com")
    training_count = 0

    training_types = ["senai", "empresa", "autonomo"]
    locations = [
        "SENAI Unidade Centro",
        "SENAI Unidade Norte",
        "Empresa Parceira",
        "Home Office",
        None,
    ]
    statuses = ["validated", "validated", "validated", "pending", "rejected"]  # Maioria validado

    for enrollment_key, enrollment_id in enrollment_ids.items():
        comp_email, modality_code = enrollment_key.rsplit("_", 1)
        competitor_id = competitor_ids.get(comp_email)
        modality_id = modality_ids.get(modality_code)

        if not competitor_id or not modality_id:
            continue

        # Criar 10-20 sessões de treino por matrícula
        num_sessions = random.randint(10, 20)

        for i in range(num_sessions):
            session_id = str(uuid4())
            training_date = date.today() - timedelta(days=random.randint(1, 120))
            hours = round(random.uniform(2, 8), 1)
            status = random.choice(statuses)

            validated_by = evaluator_id if status == "validated" else None
            validated_at = now if status == "validated" else None
            rejection_reason = "Evidências insuficientes" if status == "rejected" else None

            await session.execute(
                text(
                    """
                    INSERT INTO training_sessions (id, competitor_id, modality_id, enrollment_id, training_date, hours,
                        training_type, location, description, status, validated_by, validated_at, rejection_reason, created_at, updated_at)
                    VALUES (:id, :competitor_id, :modality_id, :enrollment_id, :training_date, :hours,
                        :training_type, :location, :description, :status, :validated_by, :validated_at, :rejection_reason, :created_at, :updated_at)
                """
                ),
                {
                    "id": session_id,
                    "competitor_id": competitor_id,
                    "modality_id": modality_id,
                    "enrollment_id": enrollment_id,
                    "training_date": training_date,
                    "hours": hours,
                    "training_type": random.choice(training_types),
                    "location": random.choice(locations),
                    "description": f"Treinamento de {modality_code} - Sessão {i+1}",
                    "status": status,
                    "validated_by": validated_by,
                    "validated_at": validated_at,
                    "rejection_reason": rejection_reason,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            training_count += 1

    await session.commit()
    print(f"✓ {training_count} sessões de treinamento criadas")


async def main():
    """Função principal para executar o seed."""
    print("\n" + "=" * 50)
    print("SEED DATABASE - SPSkills")
    print("=" * 50 + "\n")

    # Criar engine e sessão
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Limpar tabelas existentes
            print("Limpando dados existentes...")
            await clear_tables(session)

            # Executar seeds em ordem
            print("\nPopulando banco de dados...")
            user_ids = await seed_users(session)
            await seed_training_type_configs(session)
            modality_ids = await seed_modalities(session)
            competence_ids = await seed_competences(session, modality_ids)
            competitor_ids = await seed_competitors(session, user_ids)
            enrollment_ids = await seed_enrollments(session, competitor_ids, modality_ids, user_ids)
            exam_ids = await seed_exams(session, modality_ids, competence_ids, user_ids)
            await seed_grades(
                session,
                exam_ids,
                competitor_ids,
                competence_ids,
                modality_ids,
                enrollment_ids,
                user_ids,
            )
            await seed_training_sessions(
                session, competitor_ids, modality_ids, enrollment_ids, user_ids
            )

            print("\n" + "=" * 50)
            print("✅ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 50)
            print("\n📋 Credenciais de teste:")
            print("-" * 50)
            print("| Perfil      | Email                    | Senha          |")
            print("-" * 50)
            print("| Admin       | admin@spskills.com       | Admin123!      |")
            print("| Avaliador   | avaliador@spskills.com   | Avaliador123!  |")
            print("| Avaliador 2 | avaliador2@spskills.com  | Avaliador123!  |")
            print("| Competidor  | competidor@spskills.com  | Competidor123! |")
            print("| Competidor 2| competidor2@spskills.com | Competidor123! |")
            print("-" * 50)
            print("\n")

        except Exception as e:
            print(f"\n❌ Erro durante o seed: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
