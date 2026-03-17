"""
Script para popular o banco de dados com dados de teste ricos.

Uso:
    cd ct-spskills-914
    python -m scripts.seed_database

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

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    from src.config.settings import get_settings

    settings = get_settings()
    DATABASE_URL = settings.database_url
except ImportError:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/ct_spskills"
    )

random.seed(42)


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def utc_now() -> datetime:
    return datetime.now(UTC)


def d(year: int, month: int, day: int) -> date:
    return date(year, month, day)


# ============================================================
# USUÁRIOS
# ============================================================
COMPETITOR_NAMES = [
    ("João Santos", "competidor@spskills.com"),
    ("Maria Souza", "competidor2@spskills.com"),
    ("Pedro Lima", "competidor3@spskills.com"),
    ("Ana Clara Ferreira", "competidor4@spskills.com"),
    ("Lucas Mendes", "competidor5@spskills.com"),
    ("Fernanda Costa", "competidor6@spskills.com"),
    ("Rafael Oliveira", "competidor7@spskills.com"),
    ("Juliana Pereira", "competidor8@spskills.com"),
    ("Bruno Almeida", "competidor9@spskills.com"),
    ("Camila Rodrigues", "competidor10@spskills.com"),
    ("Thiago Nascimento", "competidor11@spskills.com"),
    ("Larissa Martins", "competidor12@spskills.com"),
    ("Diego Carvalho", "competidor13@spskills.com"),
    ("Aline Barbosa", "competidor14@spskills.com"),
    ("Matheus Gomes", "competidor15@spskills.com"),
]

USERS = (
    [
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
    ]
    + [
        {
            "id": str(uuid4()),
            "email": email,
            "password": "Competidor123!",
            "full_name": name,
            "role": "competitor",
            "status": "active",
        }
        for name, email in COMPETITOR_NAMES
    ]
)

# ============================================================
# MODALIDADES
# ============================================================
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

# ============================================================
# COMPETÊNCIAS (com sub-competências para algumas)
# ============================================================
COMPETENCES = {
    "SOLD": [
        {
            "name": "Soldagem TIG",
            "description": "Técnicas de soldagem TIG em diversos materiais",
            "weight": 1.5,
            "max_score": 100,
            "subs": [
                {"name": "TIG Aço Inox", "max_score": 100},
                {"name": "TIG Alumínio", "max_score": 100},
                {"name": "TIG Aço Carbono", "max_score": 100},
            ],
        },
        {
            "name": "Soldagem MIG/MAG",
            "description": "Processos de soldagem MIG e MAG",
            "weight": 1.5,
            "max_score": 100,
            "subs": [
                {"name": "MIG Curto Circuito", "max_score": 100},
                {"name": "MAG Globular", "max_score": 100},
            ],
        },
        {
            "name": "Leitura de Desenho",
            "description": "Interpretação de desenhos técnicos de soldagem",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Segurança do Trabalho",
            "description": "Normas e práticas de segurança em soldagem",
            "weight": 0.5,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Qualidade de Acabamento",
            "description": "Avaliação visual e dimensional da solda",
            "weight": 1.5,
            "max_score": 100,
            "subs": [],
        },
    ],
    "USIN": [
        {
            "name": "Programação CNC",
            "description": "Programação de tornos CNC",
            "weight": 2.0,
            "max_score": 100,
            "subs": [
                {"name": "Programação G-Code", "max_score": 100},
                {"name": "Ciclos Fixos", "max_score": 100},
                {"name": "Subprogramas", "max_score": 100},
            ],
        },
        {
            "name": "Metrologia",
            "description": "Medição e controle dimensional",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Setup de Máquina",
            "description": "Preparação e ajuste de máquinas",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Acabamento Superficial",
            "description": "Qualidade do acabamento das peças",
            "weight": 1.5,
            "max_score": 100,
            "subs": [],
        },
    ],
    "CAD": [
        {
            "name": "Modelagem 3D",
            "description": "Criação de modelos 3D paramétricos",
            "weight": 2.0,
            "max_score": 100,
            "subs": [
                {"name": "Sólidos Paramétricos", "max_score": 100},
                {"name": "Superfícies", "max_score": 100},
            ],
        },
        {
            "name": "Detalhamento Técnico",
            "description": "Criação de desenhos técnicos detalhados",
            "weight": 1.5,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Montagem",
            "description": "Montagem de conjuntos mecânicos",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Normas Técnicas",
            "description": "Aplicação de normas ABNT e ISO",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
    ],
    "ELET": [
        {
            "name": "Instalação Residencial",
            "description": "Instalações elétricas residenciais",
            "weight": 1.5,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Instalação Industrial",
            "description": "Instalações elétricas industriais",
            "weight": 1.5,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Comandos Elétricos",
            "description": "Montagem de painéis e comandos",
            "weight": 1.5,
            "max_score": 100,
            "subs": [
                {"name": "Partida Direta", "max_score": 100},
                {"name": "Inversão de Marcha", "max_score": 100},
                {"name": "Soft Starter", "max_score": 100},
            ],
        },
        {
            "name": "NR-10",
            "description": "Segurança em instalações elétricas",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
    ],
    "MECA": [
        {
            "name": "Pneumática",
            "description": "Sistemas pneumáticos industriais",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Hidráulica",
            "description": "Sistemas hidráulicos",
            "weight": 1.0,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "CLP",
            "description": "Programação de CLPs",
            "weight": 2.0,
            "max_score": 100,
            "subs": [
                {"name": "Ladder Básico", "max_score": 100},
                {"name": "Blocos de Função", "max_score": 100},
                {"name": "SCADA", "max_score": 100},
            ],
        },
        {
            "name": "Robótica",
            "description": "Programação de robôs industriais",
            "weight": 1.5,
            "max_score": 100,
            "subs": [],
        },
        {
            "name": "Integração de Sistemas",
            "description": "Integração de subsistemas mecatrônicos",
            "weight": 1.5,
            "max_score": 100,
            "subs": [],
        },
    ],
}

# ============================================================
# SIMULADOS — 17 ao longo de Out/2025 a Mar/2026
# ============================================================
EXAM_TEMPLATES = [
    {"name": "Simulado Inicial",           "type": "simulation",  "exam_date": d(2025, 10,  5)},
    {"name": "Avaliação Prática Out/25",   "type": "practical",   "exam_date": d(2025, 10, 20)},
    {"name": "Prova Teórica Nov/25",       "type": "theoretical", "exam_date": d(2025, 11,  8)},
    {"name": "Simulado Regional Nov/25",   "type": "simulation",  "exam_date": d(2025, 11, 22)},
    {"name": "Avaliação Mista Nov/25",     "type": "mixed",       "exam_date": d(2025, 11, 29)},
    {"name": "Simulado Dez/25",            "type": "simulation",  "exam_date": d(2025, 12,  6)},
    {"name": "Prova Final 2025",           "type": "practical",   "exam_date": d(2025, 12, 20)},
    {"name": "Simulado Abertura Jan/26",   "type": "simulation",  "exam_date": d(2026,  1, 10)},
    {"name": "Avaliação Prática Jan/26",   "type": "practical",   "exam_date": d(2026,  1, 25)},
    {"name": "Simulado Fev/26 — Fase 1",  "type": "simulation",  "exam_date": d(2026,  2,  7)},
    {"name": "Prova Teórica Fev/26",       "type": "theoretical", "exam_date": d(2026,  2, 14)},
    {"name": "Simulado Fev/26 — Fase 2",  "type": "simulation",  "exam_date": d(2026,  2, 21)},
    {"name": "Avaliação Mista Fev/26",     "type": "mixed",       "exam_date": d(2026,  2, 28)},
    {"name": "Simulado Mar/26 — Fase 1",  "type": "simulation",  "exam_date": d(2026,  3,  7)},
    {"name": "Avaliação Prática Mar/26",   "type": "practical",   "exam_date": d(2026,  3, 14)},
    {"name": "Simulado Nacional Mar/26",   "type": "simulation",  "exam_date": d(2026,  3, 21)},
    {"name": "Simulado Final Mar/26",      "type": "mixed",       "exam_date": d(2026,  3, 28)},
]

TRAINING_TYPE_CONFIGS = [
    {"code": "senai",    "name": "SENAI",  "description": "Treinamento nas dependências do SENAI", "display_order": 1},
    {"code": "external", "name": "FORA",   "description": "Treinamento fora do SENAI",              "display_order": 2},
]


# ============================================================
# HELPERS
# ============================================================
def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def gauss_score(mean: float, std: float = 8.0) -> float:
    return round(clamp(random.gauss(mean, std), 0, 100), 1)


# ============================================================
# FUNÇÕES DE SEED
# ============================================================
async def clear_tables(session: AsyncSession) -> None:
    tables = [
        "grade_audit_logs", "grades", "exam_competences", "exams",
        "training_sessions", "evidences", "enrollments",
        "sub_competences", "competences", "competitors", "modalities",
        "training_type_configs", "refresh_tokens", "users",
    ]
    for table in tables:
        try:
            await session.execute(text(f"DELETE FROM {table}"))  # nosec B608
        except Exception as e:
            print(f"  aviso: {table} -> {e}")
    await session.commit()
    print("Tabelas limpas")


async def seed_users(session: AsyncSession) -> dict:
    user_ids: dict = {}
    now = utc_now()
    for user in USERS:
        hashed = hash_password(user["password"])
        user_ids[user["email"]] = user["id"]
        await session.execute(
            text("""
                INSERT INTO users (id, email, password_hash, full_name, role, status, created_at, updated_at)
                VALUES (:id, :email, :password_hash, :full_name, :role, :status, :created_at, :updated_at)
            """),
            {
                "id": user["id"], "email": user["email"], "password_hash": hashed,
                "full_name": user["full_name"], "role": user["role"],
                "status": user["status"], "created_at": now, "updated_at": now,
            },
        )
    await session.commit()
    print(f"  {len(USERS)} usuarios criados")
    return user_ids


async def seed_training_type_configs(session: AsyncSession) -> None:
    now = utc_now()
    for config in TRAINING_TYPE_CONFIGS:
        await session.execute(
            text("""
                INSERT INTO training_type_configs (id, code, name, description, is_active, display_order, created_at, updated_at)
                VALUES (:id, :code, :name, :description, :is_active, :display_order, :created_at, :updated_at)
            """),
            {
                "id": str(uuid4()), "code": config["code"], "name": config["name"],
                "description": config["description"], "is_active": True,
                "display_order": config["display_order"], "created_at": now, "updated_at": now,
            },
        )
    await session.commit()
    print(f"  {len(TRAINING_TYPE_CONFIGS)} tipos de treinamento criados")


async def seed_modalities(session: AsyncSession) -> dict:
    modality_ids: dict = {}
    now = utc_now()
    for m in MODALITIES:
        modality_ids[m["code"]] = m["id"]
        await session.execute(
            text("""
                INSERT INTO modalities (id, code, name, description, is_active, min_training_hours, created_at, updated_at)
                VALUES (:id, :code, :name, :description, :is_active, :min_training_hours, :created_at, :updated_at)
            """),
            {
                "id": m["id"], "code": m["code"], "name": m["name"],
                "description": m["description"], "is_active": m["is_active"],
                "min_training_hours": m["min_training_hours"], "created_at": now, "updated_at": now,
            },
        )
    await session.commit()
    print(f"  {len(MODALITIES)} modalidades criadas")
    return modality_ids


async def seed_competences(session: AsyncSession, modality_ids: dict) -> tuple[dict, dict]:
    """Returns (competence_ids_by_code, sub_competence_ids_by_competence_id)."""
    comp_ids: dict = {}
    sub_ids: dict = {}
    now = utc_now()
    total_comp = 0
    total_sub = 0

    for mod_code, competences in COMPETENCES.items():
        modality_id = modality_ids.get(mod_code)
        if not modality_id:
            continue
        comp_ids[mod_code] = []

        for comp in competences:
            comp_id = str(uuid4())
            comp_ids[mod_code].append(comp_id)
            await session.execute(
                text("""
                    INSERT INTO competences (id, modality_id, name, description, weight, max_score, is_active, created_at, updated_at)
                    VALUES (:id, :modality_id, :name, :description, :weight, :max_score, :is_active, :created_at, :updated_at)
                """),
                {
                    "id": comp_id, "modality_id": modality_id,
                    "name": comp["name"], "description": comp["description"],
                    "weight": comp["weight"], "max_score": comp["max_score"],
                    "is_active": True, "created_at": now, "updated_at": now,
                },
            )
            total_comp += 1

            # Sub-competências
            sub_ids[comp_id] = []
            for sub in comp.get("subs", []):
                sub_id = str(uuid4())
                sub_ids[comp_id].append(sub_id)
                await session.execute(
                    text("""
                        INSERT INTO sub_competences (id, competence_id, name, max_score, created_at, updated_at)
                        VALUES (:id, :competence_id, :name, :max_score, :created_at, :updated_at)
                    """),
                    {
                        "id": sub_id, "competence_id": comp_id,
                        "name": sub["name"], "max_score": sub["max_score"],
                        "created_at": now, "updated_at": now,
                    },
                )
                total_sub += 1

    await session.commit()
    print(f"  {total_comp} competencias + {total_sub} sub-competencias criadas")
    return comp_ids, sub_ids


async def seed_competitors(session: AsyncSession, user_ids: dict) -> dict:
    competitor_ids: dict = {}
    now = utc_now()
    competitor_users = [u for u in USERS if u["role"] == "competitor"]

    for user in competitor_users:
        comp_id = str(uuid4())
        competitor_ids[user["email"]] = comp_id
        birth_year = random.randint(1999, 2006)
        birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        await session.execute(
            text("""
                INSERT INTO competitors (id, user_id, full_name, birth_date, document_number, phone, is_active, created_at, updated_at)
                VALUES (:id, :user_id, :full_name, :birth_date, :document_number, :phone, :is_active, :created_at, :updated_at)
            """),
            {
                "id": comp_id, "user_id": user_ids[user["email"]],
                "full_name": user["full_name"], "birth_date": birth_date,
                "document_number": f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}",
                "phone": f"({random.randint(11,99)}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "is_active": True, "created_at": now, "updated_at": now,
            },
        )
    await session.commit()
    print(f"  {len(competitor_ids)} competidores criados")
    return competitor_ids


async def seed_enrollments(
    session: AsyncSession,
    competitor_ids: dict,
    modality_ids: dict,
    user_ids: dict,
) -> dict:
    enrollment_ids: dict = {}
    now = utc_now()
    evaluator_id = user_ids["avaliador@spskills.com"]
    evaluator2_id = user_ids["avaliador2@spskills.com"]

    comp_list = list(competitor_ids.items())
    mod_list = list(modality_ids.items())
    counter = 0

    for comp_email, comp_id in comp_list:
        # cada competidor em 1 ou 2 modalidades
        num_mods = random.randint(1, 2)
        selected = random.sample(mod_list, num_mods)
        for mod_code, mod_id in selected:
            enroll_id = str(uuid4())
            enrollment_ids[f"{comp_email}_{mod_code}"] = enroll_id
            counter += 1
            eval_id = evaluator_id if counter % 2 == 1 else evaluator2_id
            enrolled_date = date(2025, random.randint(9, 11), random.randint(1, 28))
            await session.execute(
                text("""
                    INSERT INTO enrollments (id, competitor_id, modality_id, evaluator_id, enrolled_at, status, created_at, updated_at)
                    VALUES (:id, :competitor_id, :modality_id, :evaluator_id, :enrolled_at, :status, :created_at, :updated_at)
                """),
                {
                    "id": enroll_id, "competitor_id": comp_id, "modality_id": mod_id,
                    "evaluator_id": eval_id, "enrolled_at": enrolled_date,
                    "status": "active", "created_at": now, "updated_at": now,
                },
            )
    await session.commit()
    print(f"  {len(enrollment_ids)} matriculas criadas")
    return enrollment_ids


async def seed_exams(
    session: AsyncSession,
    modality_ids: dict,
    comp_ids: dict,
    user_ids: dict,
) -> dict:
    exam_ids: dict = {}  # mod_code -> list of (exam_id, exam_date)
    now = utc_now()
    evaluator_id = user_ids["avaliador@spskills.com"]

    for mod_code, mod_id in modality_ids.items():
        exam_ids[mod_code] = []
        for tmpl in EXAM_TEMPLATES:
            exam_id = str(uuid4())
            exam_ids[mod_code].append((exam_id, tmpl["exam_date"]))
            await session.execute(
                text("""
                    INSERT INTO exams (id, name, description, modality_id, assessment_type, exam_date, is_active, created_by, created_at, updated_at)
                    VALUES (:id, :name, :description, :modality_id, :assessment_type, :exam_date, :is_active, :created_by, :created_at, :updated_at)
                """),
                {
                    "id": exam_id,
                    "name": f"{tmpl['name']} - {mod_code}",
                    "description": f"Avaliacao {tmpl['type']} para {mod_code}",
                    "modality_id": mod_id,
                    "assessment_type": tmpl["type"],
                    "exam_date": tmpl["exam_date"],
                    "is_active": True,
                    "created_by": evaluator_id,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            for cid in comp_ids.get(mod_code, []):
                await session.execute(
                    text("INSERT INTO exam_competences (exam_id, competence_id) VALUES (:eid, :cid)"),
                    {"eid": exam_id, "cid": cid},
                )

    await session.commit()
    total = sum(len(v) for v in exam_ids.values())
    print(f"  {total} exames criados ({len(EXAM_TEMPLATES)} por modalidade)")
    return exam_ids


async def seed_grades(
    session: AsyncSession,
    exam_ids: dict,
    competitor_ids: dict,
    comp_ids: dict,
    sub_ids: dict,
    enrollment_ids: dict,
    user_ids: dict,
) -> None:
    now = utc_now()
    evaluator_id = user_ids["avaliador@spskills.com"]
    evaluator2_id = user_ids["avaliador2@spskills.com"]
    grade_count = 0

    # Perfis de evolução: alguns melhoram, outros são estáveis, alguns oscilam
    profiles = ["improving", "stable_high", "stable_mid", "oscillating", "late_bloomer"]

    # Atribuir perfil a cada competidor
    comp_profile: dict = {}
    for email in competitor_ids:
        comp_profile[email] = random.choice(profiles)

    notes_pool = [
        "Bom desempenho", "Precisa melhorar acabamento", "Excelente execucao",
        "Atencao aos detalhes", "Dentro do esperado", "Superou expectativas",
        "Precisa de mais pratica", "Evolucao notavel", None, None,
    ]

    for enroll_key in enrollment_ids:
        comp_email, mod_code = enroll_key.rsplit("_", 1)
        comp_id = competitor_ids.get(comp_email)
        if not comp_id or mod_code not in exam_ids:
            continue

        profile = comp_profile.get(comp_email, "stable_mid")

        # Base score por perfil
        base_scores = {
            "improving":    [55, 58, 62, 65, 68, 70, 72, 75, 78, 80, 82, 84, 86, 88, 89, 90, 91],
            "stable_high":  [85, 87, 84, 88, 86, 89, 87, 90, 88, 91, 89, 90, 88, 92, 90, 91, 93],
            "stable_mid":   [70, 72, 68, 74, 71, 73, 75, 72, 74, 76, 73, 75, 77, 74, 76, 78, 75],
            "oscillating":  [60, 80, 55, 85, 65, 78, 50, 88, 62, 82, 58, 86, 63, 79, 55, 84, 70],
            "late_bloomer": [55, 57, 56, 58, 59, 60, 62, 65, 70, 75, 80, 83, 85, 87, 89, 91, 93],
        }
        scores_over_time = base_scores[profile]

        exams_sorted = sorted(exam_ids[mod_code], key=lambda x: x[1])

        for idx, (exam_id, _exam_date) in enumerate(exams_sorted):
            mean = scores_over_time[min(idx, len(scores_over_time) - 1)]
            eval_id = evaluator_id if idx % 2 == 0 else evaluator2_id

            for cid in comp_ids.get(mod_code, []):
                subs = sub_ids.get(cid, [])

                if subs:
                    # Gravar notas por sub-competência (escala 0-100)
                    for sub_id in subs:
                        sub_score = gauss_score(mean)
                        await session.execute(
                            text("""
                                INSERT INTO grades (id, exam_id, competitor_id, competence_id, sub_competence_id, score, notes, created_by, updated_by, created_at, updated_at)
                                VALUES (:id, :exam_id, :competitor_id, :competence_id, :sub_competence_id, :score, :notes, :created_by, :updated_by, :created_at, :updated_at)
                            """),
                            {
                                "id": str(uuid4()), "exam_id": exam_id,
                                "competitor_id": comp_id, "competence_id": cid,
                                "sub_competence_id": sub_id,
                                "score": sub_score,
                                "notes": random.choice(notes_pool),
                                "created_by": eval_id, "updated_by": eval_id,
                                "created_at": now, "updated_at": now,
                            },
                        )
                        grade_count += 1
                else:
                    # Gravar nota direto na competência
                    score = gauss_score(mean)
                    await session.execute(
                        text("""
                            INSERT INTO grades (id, exam_id, competitor_id, competence_id, sub_competence_id, score, notes, created_by, updated_by, created_at, updated_at)
                            VALUES (:id, :exam_id, :competitor_id, :competence_id, :sub_competence_id, :score, :notes, :created_by, :updated_by, :created_at, :updated_at)
                        """),
                        {
                            "id": str(uuid4()), "exam_id": exam_id,
                            "competitor_id": comp_id, "competence_id": cid,
                            "sub_competence_id": None,
                            "score": score,
                            "notes": random.choice(notes_pool),
                            "created_by": eval_id, "updated_by": eval_id,
                            "created_at": now, "updated_at": now,
                        },
                    )
                    grade_count += 1

    await session.commit()
    print(f"  {grade_count} notas criadas")


async def seed_training_sessions(
    session: AsyncSession,
    competitor_ids: dict,
    modality_ids: dict,
    enrollment_ids: dict,
    user_ids: dict,
) -> None:
    now = utc_now()
    evaluator_id = user_ids["avaliador@spskills.com"]
    training_count = 0

    locations = ["SENAI Unidade Centro", "SENAI Unidade Norte", "Empresa Parceira", "Home Office", None]
    statuses_weighted = ["approved"] * 7 + ["pending"] * 2 + ["rejected"] * 1

    # Gerar sessões distribuídas por mês: Out/25 a Mar/26
    month_ranges = [
        (2025, 10, 1, 31), (2025, 11, 1, 30), (2025, 12, 1, 31),
        (2026,  1, 1, 31), (2026,  2, 1, 28), (2026,  3, 1, 28),
    ]

    for enroll_key, enroll_id in enrollment_ids.items():
        comp_email, mod_code = enroll_key.rsplit("_", 1)
        comp_id = competitor_ids.get(comp_email)
        mod_id = modality_ids.get(mod_code)
        if not comp_id or not mod_id:
            continue

        for year, month, day_min, day_max in month_ranges:
            # 3 a 6 sessões por mês por matrícula
            num_sessions = random.randint(3, 6)
            for _ in range(num_sessions):
                session_id = str(uuid4())
                day = random.randint(day_min, day_max)
                training_date = date(year, month, day)
                hours = round(random.uniform(2.0, 8.0), 1)
                status = random.choice(statuses_weighted)
                validated_by = evaluator_id if status == "approved" else None
                validated_at = now if status == "approved" else None
                rejection_reason = "Evidencias insuficientes" if status == "rejected" else None
                ttype = random.choice(["senai", "external"])

                await session.execute(
                    text("""
                        INSERT INTO training_sessions (
                            id, competitor_id, modality_id, enrollment_id, training_date, hours,
                            training_type, location, description, status,
                            validated_by, validated_at, rejection_reason, created_at, updated_at
                        ) VALUES (
                            :id, :competitor_id, :modality_id, :enrollment_id, :training_date, :hours,
                            :training_type, :location, :description, :status,
                            :validated_by, :validated_at, :rejection_reason, :created_at, :updated_at
                        )
                    """),
                    {
                        "id": session_id, "competitor_id": comp_id, "modality_id": mod_id,
                        "enrollment_id": enroll_id, "training_date": training_date,
                        "hours": hours, "training_type": ttype,
                        "location": random.choice(locations),
                        "description": f"Treinamento {mod_code} - {year}/{month:02d}",
                        "status": status, "validated_by": validated_by,
                        "validated_at": validated_at, "rejection_reason": rejection_reason,
                        "created_at": now, "updated_at": now,
                    },
                )
                training_count += 1

    await session.commit()
    print(f"  {training_count} sessoes de treinamento criadas (Out/25 a Mar/26)")


async def main() -> None:
    print("\n" + "=" * 55)
    print("  SEED DATABASE RICO - SPSkills")
    print("=" * 55 + "\n")

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("Limpando dados existentes...")
            await clear_tables(session)

            print("\nPopulando banco...")
            user_ids = await seed_users(session)
            await seed_training_type_configs(session)
            modality_ids = await seed_modalities(session)
            comp_ids, sub_ids = await seed_competences(session, modality_ids)
            competitor_ids = await seed_competitors(session, user_ids)
            enrollment_ids = await seed_enrollments(session, competitor_ids, modality_ids, user_ids)
            exam_ids = await seed_exams(session, modality_ids, comp_ids, user_ids)
            await seed_grades(session, exam_ids, competitor_ids, comp_ids, sub_ids, enrollment_ids, user_ids)
            await seed_training_sessions(session, competitor_ids, modality_ids, enrollment_ids, user_ids)

            print("\n" + "=" * 55)
            print("  SEED CONCLUIDO!")
            print("=" * 55)
            print()
            print("Credenciais:")
            print("  admin@spskills.com        / Admin123!")
            print("  avaliador@spskills.com    / Avaliador123!")
            print("  avaliador2@spskills.com   / Avaliador123!")
            print("  competidor@spskills.com   / Competidor123!")
            print(f"  + {len(COMPETITOR_NAMES) - 1} outros competidores (Competidor123!)")
            print()

        except Exception as e:
            print(f"\nERRO durante seed: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
