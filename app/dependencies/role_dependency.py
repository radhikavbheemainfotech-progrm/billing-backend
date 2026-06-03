from fastapi import Depends,HTTPException,status
from app.database.models import User
from app.dependencies.auth_dependency import get_current_user

def require_role(*roles: str):
    """Factory that returns a dependency enforcing one of the given roles."""

    def _checker(current_user: User = Depends(get_current_user)) -> User:

        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied.Required role(s): {roles}",
            )
        return current_user
    
    return _checker

require_admin = require_role("admin")
require_staff = require_role("staff")
require_accountant = require_role("admin","staff")

require_staff_or_admin = require_role(
    "admin",
    "staff"
)


require_all_staff = require_role(
    "admin",
    "staff",
    "accountant"
)