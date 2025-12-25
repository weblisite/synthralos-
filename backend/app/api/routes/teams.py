"""
Team Management API Routes

Handles team creation, member management, and invitations.
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import EmailStr
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import TeamInvitation, TeamMember, User
from app.services.team_service import TeamService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teams", tags=["teams"])


# ============================================================================
# Team CRUD Operations
# ============================================================================


@router.post("", status_code=status.HTTP_201_CREATED)
def create_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    name: str = Body(...),
    slug: str | None = Body(None),
    description: str | None = Body(None),
) -> Any:
    """Create a new team"""
    team_service = TeamService(session)
    team = team_service.create_team(
        name=name,
        slug=slug,
        description=description,
        owner_id=current_user.id,
    )
    return team


@router.get("")
def list_teams(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """List all teams the current user belongs to"""
    team_service = TeamService(session)
    teams = team_service.list_user_teams(current_user.id)
    return {"teams": teams, "count": len(teams)}


@router.get("/{team_id}")
def get_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> Any:
    """Get team details"""
    team_service = TeamService(session)
    team = team_service.get_team(team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check if user is a member
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    return team


@router.patch("/{team_id}")
def update_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    name: str | None = Body(None),
    description: str | None = Body(None),
    is_active: bool | None = Body(None),
) -> Any:
    """Update team details (owner/admin only)"""
    team_service = TeamService(session)
    team = team_service.get_team(team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check permissions
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners and admins can update team details",
        )

    if name is not None:
        team.name = name
    if description is not None:
        team.description = description
    if is_active is not None:
        team.is_active = is_active

    from datetime import datetime, timezone

    team.updated_at = datetime.now(timezone.utc)

    session.add(team)
    session.commit()
    session.refresh(team)

    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> None:
    """Delete a team (owner only)"""
    team_service = TeamService(session)
    team = team_service.get_team(team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check if user is owner
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owner can delete the team",
        )

    session.delete(team)
    session.commit()


# ============================================================================
# Team Member Operations
# ============================================================================


@router.get("/{team_id}/members")
def list_team_members(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> Any:
    """List all team members"""
    team_service = TeamService(session)

    # Check if user is a member
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    members = team_service.list_team_members(team_id=team_id)
    return {"members": members, "count": len(members)}


@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
def add_team_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    user_id: uuid.UUID = Body(...),
    role: str = Body("member"),
) -> Any:
    """Add a user to a team (admin/owner only)"""
    team_service = TeamService(session)

    # Check permissions
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners and admins can add members",
        )

    team_member = team_service.add_member(
        team_id=team_id,
        user_id=user_id,
        role=role,
        invited_by=current_user.id,
    )

    return team_member


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Remove a user from a team (admin/owner only)"""
    team_service = TeamService(session)

    # Check permissions
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners and admins can remove members",
        )

    # Don't allow removing yourself if you're the owner
    if user_id == current_user.id:
        team = team_service.get_team(team_id)
        if team and team.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team owner cannot remove themselves",
            )

    success = team_service.remove_member(team_id=team_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found"
        )


@router.patch("/{team_id}/members/{user_id}/role")
def update_member_role(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str = Body(...),
) -> Any:
    """Update a team member's role (owner/admin only)"""
    team_service = TeamService(session)

    # Check permissions
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners and admins can update member roles",
        )

    team_member = team_service.update_member_role(
        team_id=team_id, user_id=user_id, role=role
    )

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found"
        )

    return team_member


# ============================================================================
# Team Invitation Operations
# ============================================================================


@router.post("/{team_id}/invitations", status_code=status.HTTP_201_CREATED)
def create_invitation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    email: EmailStr = Body(...),
    role: str = Body("member"),
    expires_in_hours: int = Body(168),  # 7 days default
) -> Any:
    """Create and send a team invitation"""
    team_service = TeamService(session)

    # Check permissions
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners and admins can send invitations",
        )

    team = team_service.get_team(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Create invitation
    invitation = team_service.create_invitation(
        team_id=team_id,
        email=email,
        role=role,
        invited_by=current_user.id,
        expires_in_hours=expires_in_hours,
    )

    # Send invitation email
    inviter = session.get(User, current_user.id)
    inviter_name = (
        inviter.full_name
        if inviter and inviter.full_name
        else inviter.email
        if inviter
        else "Team Owner"
    )
    email_sent = team_service.send_invitation_email(
        invitation=invitation,
        team=team,
        inviter_name=inviter_name,
    )

    if not email_sent:
        logger.warning(f"Failed to send invitation email to {email}")

    return {"invitation": invitation, "email_sent": email_sent}


@router.get("/{team_id}/invitations")
def list_team_invitations(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    include_accepted: bool = False,
) -> Any:
    """List team invitations (admin/owner only)"""
    team_service = TeamService(session)

    # Check permissions
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current_user.id
        )
    ).first()

    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners and admins can view invitations",
        )

    invitations = team_service.list_team_invitations(
        team_id=team_id, include_accepted=include_accepted
    )
    return {"invitations": invitations, "count": len(invitations)}


@router.post("/invitations/accept", status_code=status.HTTP_200_OK)
def accept_invitation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    token: str = Body(...),
) -> Any:
    """Accept a team invitation"""
    team_service = TeamService(session)

    try:
        member = team_service.accept_invitation(token=token, user_id=current_user.id)
        return {"member": member, "message": "Invitation accepted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invitation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    invitation_id: uuid.UUID,
) -> None:
    """Revoke a team invitation (admin/owner only)"""
    team_service = TeamService(session)

    invitation = session.get(TeamInvitation, invitation_id)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
        )

    # Check permissions
    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == invitation.team_id,
            TeamMember.user_id == current_user.id,
        )
    ).first()

    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners and admins can revoke invitations",
        )

    try:
        team_service.revoke_invitation(invitation_id=invitation_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


import logging

logger = logging.getLogger(__name__)
