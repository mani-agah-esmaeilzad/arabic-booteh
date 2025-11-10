from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Sequence

import aiomysql

from .personality_seed import PERSONALITY_TEST_SEED

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    db: Optional[str] = os.getenv("DB_NAME")
    port: int = int(os.getenv("DB_PORT", "3306"))
    minsize: int = 1
    maxsize: int = int(os.getenv("DB_POOL_SIZE", "15"))
    autocommit: bool = False
    charset: str = "utf8mb4"
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))

    def to_kwargs(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "db": self.db,
            "port": self.port,
            "minsize": self.minsize,
            "maxsize": self.maxsize,
            "autocommit": self.autocommit,
            "charset": self.charset,
            "cursorclass": aiomysql.DictCursor,
            "pool_recycle": self.pool_recycle,
        }


class DatabaseManager:
    def __init__(self, config: Optional[DatabaseConfig] = None) -> None:
        self.config = config or DatabaseConfig()
        self._pool: Optional[aiomysql.Pool] = None

    async def get_pool(self) -> aiomysql.Pool:
        if self._pool is None:
            config_dict = self.config.to_kwargs()
            logger.info(
                "Creating MySQL connection pool: host=%s db=%s",
                config_dict["host"],
                config_dict.get("db"),
            )
            self._pool = await aiomysql.create_pool(**config_dict)
        return self._pool

    @asynccontextmanager
    async def connection(self):
        pool = await self.get_pool()
        conn = await pool.acquire()
        try:
            await conn.ping(reconnect=True)
            yield conn
        finally:
            pool.release(conn)

    async def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None

    async def fetch_all(
        self, query: str, params: Optional[Sequence[Any]] = None
    ) -> List[dict[str, Any]]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:  # type: ignore[call-arg]
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params or ())
                rows = await cursor.fetchall()
                return list(rows)

    async def fetch_one(
        self, query: str, params: Optional[Sequence[Any]] = None
    ) -> Optional[dict[str, Any]]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:  # type: ignore[call-arg]
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params or ())
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def execute(
        self, query: str, params: Optional[Sequence[Any]] = None
    ) -> int:
        pool = await self.get_pool()
        async with pool.acquire() as conn:  # type: ignore[call-arg]
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params or ())
                await conn.commit()
                return cursor.lastrowid or 0

    async def executemany(
        self, query: str, params_seq: Iterable[Sequence[Any]]
    ) -> None:
        pool = await self.get_pool()
        async with pool.acquire() as conn:  # type: ignore[call-arg]
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.executemany(query, list(params_seq))
                await conn.commit()

    async def test_connection(self) -> bool:
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:  # type: ignore[call-arg]
                await conn.ping(reconnect=True)
            logger.info("✅ اتصال به دیتابیس MySQL با موفقیت برقرار شد.")
            return True
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.error("❌ خطا در اتصال به دیتابیس: %s", exc)
            return False

    async def create_tables(self) -> bool:
        async with self.connection() as conn:
            try:
                await conn.begin()
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await self._initialize_schema(cursor)
                await conn.commit()
                logger.info("✅ فرآیند ایجاد جداول با موفقیت به پایان رسید.")
                return True
            except Exception as exc:
                await conn.rollback()
                logger.error("❌ خطا در هنگام ایجاد جداول: %s", exc)
                return False

    async def _initialize_schema(self, cursor: aiomysql.DictCursor) -> None:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                phone_number VARCHAR(20),
                age INT,
                education_level VARCHAR(100),
                work_experience VARCHAR(100),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        logger.info("  - جدول 'users' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        logger.info("  - جدول 'admins' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questionnaires (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                initial_prompt TEXT NOT NULL,
                persona_prompt TEXT NOT NULL,
                analysis_prompt TEXT NOT NULL,
                has_narrator BOOLEAN DEFAULT FALSE,
                character_count INT DEFAULT 1,
                has_timer BOOLEAN DEFAULT TRUE,
                timer_duration INT DEFAULT 15,
                min_questions INT DEFAULT 5,
                max_questions INT DEFAULT 8,
                display_order INT DEFAULT 0,
                category VARCHAR(100) NOT NULL DEFAULT 'مهارت‌های ارتباطی',
                next_mystery_slug VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        logger.info("  - جدول 'questionnaires' ایجاد شد.")

        await cursor.execute(
            """
            ALTER TABLE questionnaires
                ADD COLUMN IF NOT EXISTS next_mystery_slug VARCHAR(255) DEFAULT NULL AFTER category
            """
        )

        await cursor.execute(
            """
            ALTER TABLE questionnaires
                ADD COLUMN IF NOT EXISTS total_phases TINYINT DEFAULT 1 AFTER next_mystery_slug,
                ADD COLUMN IF NOT EXISTS phase_two_persona_name VARCHAR(255) DEFAULT NULL AFTER total_phases,
                ADD COLUMN IF NOT EXISTS phase_two_persona_prompt TEXT AFTER phase_two_persona_name,
                ADD COLUMN IF NOT EXISTS phase_two_analysis_prompt TEXT AFTER phase_two_persona_prompt,
                ADD COLUMN IF NOT EXISTS phase_two_welcome_message TEXT AFTER phase_two_analysis_prompt
            """
        )

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS personality_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) NOT NULL UNIQUE,
                tagline VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                report_name VARCHAR(255) NOT NULL,
                highlights TEXT NOT NULL,
                persona_name VARCHAR(255) DEFAULT 'کوچ شخصیت',
                initial_prompt TEXT,
                persona_prompt TEXT,
                analysis_prompt TEXT,
                has_timer BOOLEAN DEFAULT FALSE,
                timer_duration INT DEFAULT NULL,
                model VARCHAR(100) DEFAULT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        logger.info("  - جدول 'personality_assessments' ایجاد شد.")

        await cursor.execute(
            "ALTER TABLE personality_assessments ADD COLUMN IF NOT EXISTS persona_name VARCHAR(255) DEFAULT 'کوچ شخصیت'"
        )
        await cursor.execute(
            "ALTER TABLE personality_assessments ADD COLUMN IF NOT EXISTS initial_prompt TEXT"
        )
        await cursor.execute(
            "ALTER TABLE personality_assessments ADD COLUMN IF NOT EXISTS persona_prompt TEXT"
        )
        await cursor.execute(
            "ALTER TABLE personality_assessments ADD COLUMN IF NOT EXISTS analysis_prompt TEXT"
        )
        await cursor.execute(
            "ALTER TABLE personality_assessments ADD COLUMN IF NOT EXISTS has_timer BOOLEAN DEFAULT FALSE"
        )
        await cursor.execute(
            "ALTER TABLE personality_assessments ADD COLUMN IF NOT EXISTS timer_duration INT DEFAULT NULL"
        )
        await cursor.execute(
            "ALTER TABLE personality_assessments ADD COLUMN IF NOT EXISTS model VARCHAR(100) DEFAULT NULL"
        )

        await cursor.execute("SELECT COUNT(*) as count FROM personality_assessments")
        count_row = await cursor.fetchone()
        count = count_row["count"] if count_row else 0
        if count == 0:
            placeholders = ", ".join(["(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"] * len(PERSONALITY_TEST_SEED))
            values: List[Any] = []
            for test in PERSONALITY_TEST_SEED:
                values.extend(
                    [
                        test["name"],
                        test["slug"],
                        test["tagline"],
                        test["description"],
                        test["report_name"],
                        json.dumps(test["highlights"], ensure_ascii=False),
                        test.get("persona_name", "کوچ شخصیت"),
                        test.get("initial_prompt"),
                        test.get("persona_prompt"),
                        test.get("analysis_prompt"),
                        test.get("has_timer", False),
                        test.get("timer_duration"),
                        test.get("model"),
                        test.get("is_active", True),
                    ]
                )
            if placeholders:
                await cursor.execute(
                    f"""
                    INSERT INTO personality_assessments
                        (name, slug, tagline, description, report_name, highlights, persona_name, initial_prompt,
                         persona_prompt, analysis_prompt, has_timer, timer_duration, model, is_active)
                    VALUES {placeholders}
                    """,
                    values,
                )
                logger.info("  - داده‌های اولیه آزمون‌های شخصیتی اضافه شد.")
        else:
            for test in PERSONALITY_TEST_SEED:
                await cursor.execute(
                    """
                    UPDATE personality_assessments
                       SET tagline = %s,
                           description = %s,
                           report_name = %s,
                           highlights = %s,
                           persona_name = %s,
                           initial_prompt = %s,
                           persona_prompt = %s,
                           analysis_prompt = %s,
                           has_timer = %s,
                           timer_duration = %s,
                           model = %s,
                           is_active = %s
                     WHERE slug = %s
                    """,
                    (
                        test["tagline"],
                        test["description"],
                        test["report_name"],
                        json.dumps(test["highlights"], ensure_ascii=False),
                        test.get("persona_name", "کوچ شخصیت"),
                        test.get("initial_prompt"),
                        test.get("persona_prompt"),
                        test.get("analysis_prompt"),
                        test.get("has_timer", False),
                        test.get("timer_duration"),
                        test.get("model"),
                        test.get("is_active", True),
                        test["slug"],
                    ),
                )

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS personality_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                personality_assessment_id INT NOT NULL,
                session_uuid VARCHAR(64) NOT NULL UNIQUE,
                status ENUM('in-progress','completed','cancelled') DEFAULT 'in-progress',
                results JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (personality_assessment_id) REFERENCES personality_assessments(id) ON DELETE CASCADE
            )
            """
        )
        logger.info("  - جدول 'personality_sessions' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS personality_assessment_applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                personality_assessment_id INT NOT NULL,
                slug VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                organization VARCHAR(255),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (personality_assessment_id) REFERENCES personality_assessments(id) ON DELETE CASCADE
            )
            """
        )
        logger.info("  - جدول 'personality_assessment_applications' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                questionnaire_id INT NOT NULL,
                session_id VARCHAR(255) UNIQUE,
                status ENUM('pending','in-progress','completed') DEFAULT 'pending',
                results JSON,
                current_phase TINYINT DEFAULT 1,
                phase_total TINYINT DEFAULT 1,
                score INT,
                max_score INT DEFAULT 100,
                description TEXT,
                supplementary_answers JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id) ON DELETE CASCADE,
                UNIQUE KEY uq_user_questionnaire (user_id, questionnaire_id)
            )
            """
        )
        logger.info("  - جدول 'assessments' ایجاد شد.")

        await cursor.execute(
            """
            ALTER TABLE assessments
                ADD COLUMN IF NOT EXISTS current_phase TINYINT DEFAULT 1 AFTER results,
                ADD COLUMN IF NOT EXISTS phase_total TINYINT DEFAULT 1 AFTER current_phase
            """
        )

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                assessment_id INT NOT NULL,
                user_id INT NOT NULL,
                message_type ENUM('user', 'ai', 'system') NOT NULL,
                content TEXT NOT NULL,
                character_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        logger.info("  - جدول 'chat_messages' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS organizations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        logger.info("  - جدول 'organizations' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS organization_questionnaires (
                organization_id INT NOT NULL,
                questionnaire_id INT NOT NULL,
                PRIMARY KEY (organization_id, questionnaire_id),
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
                FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id) ON DELETE CASCADE
            )
            """
        )
        logger.info("  - جدول 'organization_questionnaires' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS organization_users (
                organization_id INT NOT NULL,
                user_id INT NOT NULL,
                PRIMARY KEY (organization_id, user_id),
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        logger.info("  - جدول 'organization_users' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                slug VARCHAR(255) NOT NULL UNIQUE,
                excerpt TEXT,
                content LONGTEXT NOT NULL,
                cover_image_url VARCHAR(500),
                author VARCHAR(100),
                is_published BOOLEAN DEFAULT TRUE,
                published_at TIMESTAMP NULL DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        logger.info("  - جدول 'blog_posts' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mystery_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) NOT NULL UNIQUE,
                short_description TEXT NOT NULL,
                intro_message TEXT NOT NULL,
                guide_name VARCHAR(255) DEFAULT 'رازمَستر',
                system_prompt TEXT NOT NULL,
                analysis_prompt TEXT,
                bubble_prompt TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        logger.info("  - جدول 'mystery_assessments' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mystery_assessment_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mystery_assessment_id INT NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                ai_notes TEXT,
                display_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (mystery_assessment_id) REFERENCES mystery_assessments(id) ON DELETE CASCADE
            )
            """
        )
        logger.info("  - جدول 'mystery_assessment_images' ایجاد شد.")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mystery_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                mystery_assessment_id INT NOT NULL,
                session_uuid VARCHAR(64) NOT NULL UNIQUE,
                status ENUM('in-progress','completed') DEFAULT 'in-progress',
                conversation JSON,
                summary JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (mystery_assessment_id) REFERENCES mystery_assessments(id) ON DELETE CASCADE
            )
            """
        )
        logger.info("  - جدول 'mystery_sessions' ایجاد شد.")

        await cursor.execute(
            """
            ALTER TABLE mystery_assessments
                ADD COLUMN IF NOT EXISTS bubble_prompt TEXT AFTER analysis_prompt
            """
        )



db_manager = DatabaseManager()


__all__ = [
    "DatabaseConfig",
    "DatabaseManager",
    "db_manager",
]
