"""
Tests for Service Layer
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.equipment import Equipment, EquipmentStatus, EquipmentCategory
from app.models.equipment_log import EquipmentLog, EquipmentLogType
from app.models.location import Location, LocationType
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.used_totp_code import UsedTotpCode
from app.services.equipment_service import EquipmentService
from app.services.auth_service import AuthService


# ==================== Fixtures ====================

@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for testing with in-memory SQLite"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    """Create async session for testing"""
    async_session = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashedpassword123",
        role="operator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_location(db_session: AsyncSession):
    """Create a test location"""
    location = Location(
        name="Test Vessel",
        code="TV001",
        location_type=LocationType.VESSEL,
        is_active=True,
    )
    db_session.add(location)
    await db_session.commit()
    await db_session.refresh(location)
    return location


@pytest_asyncio.fixture
async def test_equipment(db_session: AsyncSession, test_location: Location):
    """Create a test equipment"""
    equipment = Equipment(
        asset_code="MBES-2024-001",
        qr_code="https://example.com/e/MBES-2024-001",
        category=EquipmentCategory.MBES,
        manufacturer="Kongsberg",
        model="EM2040C",
        model_code="EM2040C",
        status=EquipmentStatus.IN_STOCK,
        current_location_id=test_location.id,
        is_active=True,
    )
    db_session.add(equipment)
    await db_session.commit()
    await db_session.refresh(equipment)
    return equipment


# ==================== EquipmentService Tests ====================

class TestEquipmentService:
    """Tests for EquipmentService"""

    @pytest.mark.asyncio
    async def test_log_equipment_change(self, db_session: AsyncSession, test_equipment: Equipment, test_user: User):
        """Test logging equipment changes"""
        service = EquipmentService(db_session)

        await service.log_equipment_change(
            equipment_id=test_equipment.id,
            log_type=EquipmentLogType.STATUS_CHANGE,
            description="Test status change",
            old_value="in_stock",
            new_value="deployed",
            user_id=test_user.id,
        )
        await db_session.commit()

        # Verify log was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(EquipmentLog).where(EquipmentLog.equipment_id == test_equipment.id)
        )
        logs = result.scalars().all()

        assert len(logs) == 1
        assert logs[0].log_type == EquipmentLogType.STATUS_CHANGE
        assert logs[0].description == "Test status change"
        assert logs[0].created_by == test_user.id

    @pytest.mark.asyncio
    async def test_get_location_info(self, db_session: AsyncSession, test_location: Location):
        """Test getting location info"""
        service = EquipmentService(db_session)

        info = await service.get_location_info(test_location.id)

        assert info is not None
        assert info["id"] == test_location.id
        assert info["name"] == "Test Vessel"
        assert info["type"] == "vessel"

    @pytest.mark.asyncio
    async def test_get_location_info_none(self, db_session: AsyncSession):
        """Test getting location info with None id"""
        service = EquipmentService(db_session)

        info = await service.get_location_info(None)

        assert info is None

    @pytest.mark.asyncio
    async def test_get_equipment_by_id(self, db_session: AsyncSession, test_equipment: Equipment):
        """Test getting equipment by ID"""
        service = EquipmentService(db_session)

        equipment = await service.get_equipment_by_id(test_equipment.id)

        assert equipment is not None
        assert equipment.id == test_equipment.id
        assert equipment.asset_code == "MBES-2024-001"

    @pytest.mark.asyncio
    async def test_get_equipment_by_asset_code(self, db_session: AsyncSession, test_equipment: Equipment):
        """Test getting equipment by asset code"""
        service = EquipmentService(db_session)

        equipment = await service.get_equipment_by_asset_code("MBES-2024-001")

        assert equipment is not None
        assert equipment.id == test_equipment.id

    @pytest.mark.asyncio
    async def test_build_status_log_json(self, db_session: AsyncSession):
        """Test building status log JSON"""
        service = EquipmentService(db_session)

        json_str = service.build_status_log_json(
            status="deployed",
            location_info={"id": 1, "name": "Test", "type": "vessel"}
        )

        import json
        parsed = json.loads(json_str)
        assert parsed["status"] == "deployed"
        assert parsed["location"]["id"] == 1

    @pytest.mark.asyncio
    async def test_add_note(self, db_session: AsyncSession, test_equipment: Equipment, test_user: User):
        """Test adding note to equipment"""
        service = EquipmentService(db_session)

        await service.add_note(
            equipment=test_equipment,
            user_id=test_user.id,
            note="Test note content"
        )
        await db_session.commit()

        # Verify log was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(EquipmentLog).where(
                EquipmentLog.equipment_id == test_equipment.id,
                EquipmentLog.log_type == EquipmentLogType.NOTE
            )
        )
        log = result.scalar_one_or_none()

        assert log is not None
        assert log.description == "Test note content"


# ==================== AuthService Tests ====================

class TestAuthService:
    """Tests for AuthService"""

    @pytest.mark.asyncio
    async def test_check_totp_reuse_not_used(self, db_session: AsyncSession, test_user: User):
        """Test TOTP reuse check when code not used"""
        service = AuthService(db_session)

        is_reused = await service.check_totp_reuse(test_user.id, "123456")

        assert is_reused is False

    @pytest.mark.asyncio
    async def test_mark_totp_used(self, db_session: AsyncSession, test_user: User):
        """Test marking TOTP as used"""
        service = AuthService(db_session)

        await service.mark_totp_used(test_user.id, "123456")
        await db_session.commit()

        # Verify it's now marked as used
        is_reused = await service.check_totp_reuse(test_user.id, "123456")
        assert is_reused is True

    @pytest.mark.asyncio
    async def test_cleanup_expired_totp_codes(self, db_session: AsyncSession, test_user: User):
        """Test cleanup of expired TOTP codes"""
        # Create an expired code
        expired_code = UsedTotpCode(
            user_id=test_user.id,
            code_hash="expired_hash",
            expires_at=datetime.utcnow() - timedelta(minutes=5),
        )
        db_session.add(expired_code)
        await db_session.commit()

        service = AuthService(db_session)
        await service.cleanup_expired_totp_codes(test_user.id)
        await db_session.commit()

        # Verify expired code was deleted
        from sqlalchemy import select
        result = await db_session.execute(
            select(UsedTotpCode).where(UsedTotpCode.user_id == test_user.id)
        )
        codes = result.scalars().all()

        assert len(codes) == 0

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session: AsyncSession, test_user: User):
        """Test getting user by username"""
        service = AuthService(db_session)

        user = await service.get_user_by_username("testuser")

        assert user is not None
        assert user.id == test_user.id
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session: AsyncSession):
        """Test getting user by username when not found"""
        service = AuthService(db_session)

        user = await service.get_user_by_username("nonexistent")

        assert user is None

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self, db_session: AsyncSession, test_user: User):
        """Test revoking all user tokens"""
        # Create some tokens
        for i in range(3):
            token = RefreshToken(
                user_id=test_user.id,
                token_hash=f"hash_{i}",
                token_family=f"family_{i}",
                expires_at=datetime.utcnow() + timedelta(days=7),
            )
            db_session.add(token)
        await db_session.commit()

        service = AuthService(db_session)
        count = await service.revoke_all_user_tokens(test_user.id, "test_logout")

        assert count == 3

        # Verify all tokens are revoked
        from sqlalchemy import select
        result = await db_session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == test_user.id,
                RefreshToken.is_revoked == False
            )
        )
        active_tokens = result.scalars().all()

        assert len(active_tokens) == 0
