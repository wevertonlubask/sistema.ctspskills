"""Script para limpar todos os dados do banco, mantendo apenas o usuário admin."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from src.infrastructure.database.connection import async_session_factory


async def cleanup_database():
    """Remove all data from the database except the admin user."""

    async with async_session_factory() as session:
        try:
            print("Iniciando limpeza do banco de dados...")

            # Disable foreign key checks temporarily (PostgreSQL)
            # Delete in order respecting foreign keys

            tables_to_clean = [
                # Audit and logs
                ("grade_audit_logs", None),
                # Grades and assessments
                ("grades", None),
                ("exams", None),
                # Training related
                ("evidences", None),
                ("training_sessions", None),
                ("training_type_configs", None),
                # Enrollments and modality relations
                ("enrollments", None),
                ("evaluator_modalities", None),
                # Goals and plans
                ("plan_items", None),
                ("training_plans", None),
                ("milestones", None),
                ("goals", None),
                # Gamification
                ("achievements", None),
                ("badges", None),
                ("user_points", None),
                # Communication
                ("messages", None),
                ("conversations", None),
                ("feedbacks", None),
                # Resources and events
                ("resources", None),
                ("schedules", None),
                ("events", None),
                ("notifications", None),
                # Competences and competitors
                ("competences", None),
                ("competitors", None),
                # Modalities
                ("modalities", None),
                # Users (except admin)
                ("refresh_tokens", None),
                ("users", "email != 'admin@spskills.com'"),
            ]

            for table_name, condition in tables_to_clean:
                try:
                    if condition:
                        query = text(f"DELETE FROM {table_name} WHERE {condition}")
                    else:
                        query = text(f"DELETE FROM {table_name}")

                    result = await session.execute(query)
                    deleted_count = result.rowcount
                    print(f"  ✓ {table_name}: {deleted_count} registros removidos")
                except Exception as e:
                    print(f"  ✗ {table_name}: Erro - {str(e)}")

            await session.commit()
            print("\n✅ Limpeza concluída com sucesso!")
            print("   Apenas o usuário admin@spskills.com foi mantido.")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Erro durante a limpeza: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(cleanup_database())
