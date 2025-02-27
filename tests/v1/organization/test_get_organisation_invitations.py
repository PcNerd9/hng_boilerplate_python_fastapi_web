from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organisation import Organisation
from api.v1.services.organisation import organisation_service
from main import app


def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

def mock_org():
    return Organisation(
        id=str(uuid7()),
        name="Test Organisation",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session


@pytest.fixture
def test_get_organisations_invitations_success(client, db_session_mock):
    """
    Test to successfully get organisation invites
    """
    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_admin
    
    with patch("api.v1.services.organisation.organisation_service.fetch_all_invitations") as mock_fetch_all_invitations:
        mock_invitations = [
            {
                "id": str(uuid7()),
                "user_id": str(uuid7()),
                "organisation_id": str(uuid7()),
                "expires_at": datetime.now(timezone.utc),
            }
        ]
        mock_fetch_all_invitations.return_value = mock_invitations
        
        response = client.get("/api/v1/organisations/invites")        
        assert response.status_code == 200
        assert response.json() == {
            "message": "Organisation invites fetched successfully",
            "data": mock_invitations,
            "success": True,
        }
        mock_fetch_all_invitations.assert_called_once()
        mock_fetch_all_invitations.assert_called_with(db_session_mock)


@pytest.fixture
def test_get_organisations_invitations_not_admin(client, db_session_mock):
    """
    Test not-admin user access to organisation invites
    """
    def mock_get_current_user():
        return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_user
    
    response = client.get("/api/v1/organisations/invites")
    
    assert response.status_code == 400
    assert response.json() == {
        "status_code": 400,
        "message": "Unable to retrieve organisations invites."
    }



