"""
Team Service

Handles team management, invitations, and member operations.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from pydantic import EmailStr
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Team, TeamInvitation, TeamMember, User
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class TeamService:
    """Service for team management operations"""

    def __init__(self, session: Session):
        self.session = session

    def create_team(
        self,
        *,
        name: str,
        slug: str | None = None,
        description: str | None = None,
        owner_id: uuid.UUID,
    ) -> Team:
        """Create a new team"""
        if not slug:
            # Generate slug from name
            slug = name.lower().replace(" ", "-").replace("_", "-")
            # Remove special characters
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            # Ensure uniqueness
            base_slug = slug
            counter = 1
            while self.session.exec(select(Team).where(Team.slug == slug)).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

        team = Team(
            name=name,
            slug=slug,
            description=description,
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Add owner as team member with owner role
        team_member = TeamMember(
            team_id=team.id,
            user_id=owner_id,
            role="owner",
            joined_at=datetime.now(timezone.utc),
        )

        self.session.add(team)
        self.session.add(team_member)
        self.session.commit()
        self.session.refresh(team)

        logger.info(f"Team created: {team.id} by user {owner_id}")
        return team

    def get_team(self, team_id: uuid.UUID) -> Team | None:
        """Get team by ID"""
        return self.session.get(Team, team_id)

    def get_team_by_slug(self, slug: str) -> Team | None:
        """Get team by slug"""
        return self.session.exec(select(Team).where(Team.slug == slug)).first()

    def list_user_teams(self, user_id: uuid.UUID) -> list[Team]:
        """List all teams a user belongs to"""
        query = (
            select(Team)
            .join(TeamMember)
            .where(TeamMember.user_id == user_id)
            .where(Team.is_active == True)  # noqa: E712
        )
        return list(self.session.exec(query).all())

    def add_member(
        self,
        *,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member",
        invited_by: uuid.UUID | None = None,
    ) -> TeamMember:
        """Add a user to a team"""
        # Check if member already exists
        existing = self.session.exec(
            select(TeamMember).where(
                TeamMember.team_id == team_id, TeamMember.user_id == user_id
            )
        ).first()

        if existing:
            # Update role if different
            if existing.role != role:
                existing.role = role
                self.session.add(existing)
                self.session.commit()
                self.session.refresh(existing)
            return existing

        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role,
            joined_at=datetime.now(timezone.utc),
            invited_by=invited_by,
        )

        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)

        logger.info(f"User {user_id} added to team {team_id} with role {role}")
        return member

    def remove_member(self, *, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove a user from a team"""
        member = self.session.exec(
            select(TeamMember).where(
                TeamMember.team_id == team_id, TeamMember.user_id == user_id
            )
        ).first()

        if not member:
            return False

        # Don't allow removing the owner
        if member.role == "owner":
            raise ValueError("Cannot remove team owner")

        self.session.delete(member)
        self.session.commit()
        logger.info(f"User {user_id} removed from team {team_id}")
        return True

    def update_member_role(
        self, *, team_id: uuid.UUID, user_id: uuid.UUID, role: str
    ) -> TeamMember | None:
        """Update a team member's role"""
        member = self.session.exec(
            select(TeamMember).where(
                TeamMember.team_id == team_id, TeamMember.user_id == user_id
            )
        ).first()

        if not member:
            return None

        # Don't allow changing owner role
        if member.role == "owner" and role != "owner":
            raise ValueError("Cannot change owner role")

        member.role = role
        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)

        logger.info(f"User {user_id} role updated to {role} in team {team_id}")
        return member

    def create_invitation(
        self,
        *,
        team_id: uuid.UUID,
        email: EmailStr,
        role: str = "member",
        invited_by: uuid.UUID,
        expires_in_hours: int = 168,  # 7 days default
    ) -> TeamInvitation:
        """Create a team invitation"""
        # Check if user already exists and is a member
        user = self.session.exec(select(User).where(User.email == email)).first()
        if user:
            existing_member = self.session.exec(
                select(TeamMember).where(
                    TeamMember.team_id == team_id, TeamMember.user_id == user.id
                )
            ).first()
            if existing_member:
                raise ValueError("User is already a team member")

        # Check for existing pending invitation
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        existing_invitation = self.session.exec(
            select(TeamInvitation).where(
                TeamInvitation.team_id == team_id,
                TeamInvitation.email == email,
                TeamInvitation.accepted_at.is_(None),
                TeamInvitation.revoked_at.is_(None),
                TeamInvitation.expires_at > datetime.now(timezone.utc),
            )
        ).first()

        if existing_invitation:
            # Update expiration if needed
            existing_invitation.expires_at = expires_at
            existing_invitation.role = role
            self.session.add(existing_invitation)
            self.session.commit()
            self.session.refresh(existing_invitation)
            return existing_invitation

        # Generate invitation token
        token = generate_token()

        invitation = TeamInvitation(
            team_id=team_id,
            email=email,
            token=token,
            role=role,
            invited_by=invited_by,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(invitation)
        self.session.commit()
        self.session.refresh(invitation)

        logger.info(f"Invitation created for {email} to team {team_id}")
        return invitation

    def send_invitation_email(
        self,
        *,
        invitation: TeamInvitation,
        team: Team,
        inviter_name: str | None = None,
    ) -> bool:
        """Send invitation email via Resend"""
        try:
            from app.services.email_template_service import email_template_service

            # Get invitation email template
            template = email_template_service.get_template_by_slug("team-invitation")
            if not template:
                # Fallback to default template
                subject = f"Invitation to join {team.name} on {settings.PROJECT_NAME}"
                html_content = self._generate_default_invitation_email(
                    invitation=invitation, team=team, inviter_name=inviter_name
                )
            else:
                # Render template
                accept_url = f"{settings.FRONTEND_HOST}/teams/invitations/accept?token={invitation.token}"
                context = {
                    "team_name": team.name,
                    "inviter_name": inviter_name or "Team Owner",
                    "accept_url": accept_url,
                    "expires_at": invitation.expires_at.isoformat(),
                    "role": invitation.role,
                    "project_name": settings.PROJECT_NAME,
                }
                subject = template_service.render_template(
                    template=template, field="subject", context=context
                )
                html_content = template_service.render_template(
                    template=template, field="html_content", context=context
                )

            return email_service.send_email(
                email_to=invitation.email,
                subject=subject,
                html_content=html_content,
            )
        except Exception as e:
            logger.error(f"Failed to send invitation email: {e}", exc_info=True)
            return False

    def _generate_default_invitation_email(
        self,
        *,
        invitation: TeamInvitation,
        team: Team,
        inviter_name: str | None = None,
    ) -> str:
        """Generate default invitation email HTML"""
        accept_url = f"{settings.FRONTEND_HOST}/teams/invitations/accept?token={invitation.token}"
        return f"""
        <html>
        <body>
            <h2>You've been invited to join {team.name}</h2>
            <p>Hello,</p>
            <p>{inviter_name or 'A team member'} has invited you to join <strong>{team.name}</strong> on {settings.PROJECT_NAME}.</p>
            <p>Your role will be: <strong>{invitation.role}</strong></p>
            <p><a href="{accept_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accept Invitation</a></p>
            <p>This invitation expires on {invitation.expires_at.strftime('%Y-%m-%d %H:%M UTC')}.</p>
            <p>If you didn't expect this invitation, you can safely ignore this email.</p>
        </body>
        </html>
        """

    def accept_invitation(self, *, token: str, user_id: uuid.UUID) -> TeamMember | None:
        """Accept a team invitation"""
        invitation = self.session.exec(
            select(TeamInvitation).where(TeamInvitation.token == token)
        ).first()

        if not invitation:
            raise ValueError("Invalid invitation token")

        if invitation.accepted_at:
            raise ValueError("Invitation already accepted")

        if invitation.revoked_at:
            raise ValueError("Invitation has been revoked")

        if invitation.expires_at < datetime.now(timezone.utc):
            raise ValueError("Invitation has expired")

        # Verify user email matches invitation email
        user = self.session.get(User, user_id)
        if not user or user.email != invitation.email:
            raise ValueError("User email does not match invitation email")

        # Add user to team
        member = self.add_member(
            team_id=invitation.team_id,
            user_id=user_id,
            role=invitation.role,
            invited_by=invitation.invited_by,
        )

        # Mark invitation as accepted
        invitation.accepted_at = datetime.now(timezone.utc)
        self.session.add(invitation)
        self.session.commit()

        logger.info(f"Invitation {invitation.id} accepted by user {user_id}")
        return member

    def revoke_invitation(self, *, invitation_id: uuid.UUID) -> bool:
        """Revoke a team invitation"""
        invitation = self.session.get(TeamInvitation, invitation_id)
        if not invitation:
            return False

        if invitation.accepted_at:
            raise ValueError("Cannot revoke accepted invitation")

        invitation.revoked_at = datetime.now(timezone.utc)
        self.session.add(invitation)
        self.session.commit()

        logger.info(f"Invitation {invitation_id} revoked")
        return True

    def list_team_invitations(
        self, *, team_id: uuid.UUID, include_accepted: bool = False
    ) -> list[TeamInvitation]:
        """List team invitations"""
        query = select(TeamInvitation).where(TeamInvitation.team_id == team_id)

        if not include_accepted:
            query = query.where(TeamInvitation.accepted_at.is_(None))

        query = query.where(TeamInvitation.revoked_at.is_(None))
        return list(
            self.session.exec(query.order_by(TeamInvitation.created_at.desc())).all()
        )

    def list_team_members(self, *, team_id: uuid.UUID) -> list[TeamMember]:
        """List all team members"""
        query = select(TeamMember).where(TeamMember.team_id == team_id)
        return list(self.session.exec(query.order_by(TeamMember.joined_at)).all())
