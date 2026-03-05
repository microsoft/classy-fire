# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import secrets
import uuid
from typing import Dict, List, Optional, Set


class ClassList:
    """A named list of classification classes that can be shared with other users."""

    def __init__(self, name: str, class_names: List[str], owner: str) -> None:
        """
        :param name: The display name of the list.
        :param class_names: The classification class names that make up the list.
        :param owner: The user ID of the list owner.
        """
        self.id: str = str(uuid.uuid4())
        self.name = name
        self.class_names = list(class_names)
        self.owner = owner
        self.members: Set[str] = {owner}

    def add_member(self, user_id: str) -> None:
        """Add a user to the list's members."""
        self.members.add(user_id)

    def is_member(self, user_id: str) -> bool:
        """Return True if the user is a member of this list."""
        return user_id in self.members


class ListRegistry:
    """
    Registry that manages classification lists, invite tokens, and pending invites.

    Typical sharing flow:
      1. An existing user calls ``share_list_with_email`` to invite someone by e-mail.
         If the invitee is not yet registered, a pending invite is stored.
      2. The invitee registers via ``register_user`` (passing their e-mail address).
         The registry detects the pending invite and automatically adds the new user
         to the shared list without any additional action on the new user's part.
      3. If the invitee already has an account they can still join via an explicit
         invite token returned by ``share_list_with_email``.
    """

    def __init__(self) -> None:
        self._lists: Dict[str, ClassList] = {}
        # invite_token -> list_id
        self._invite_tokens: Dict[str, str] = {}
        # email (lower-cased) -> list_id  (for users not yet registered)
        self._pending_invites: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # List management
    # ------------------------------------------------------------------

    def create_list(self, name: str, class_names: List[str], owner: str) -> ClassList:
        """Create a new classification list owned by *owner* and register it."""
        cls_list = ClassList(name, class_names, owner)
        self._lists[cls_list.id] = cls_list
        return cls_list

    def get_list(self, list_id: str) -> Optional[ClassList]:
        """Return the :class:`ClassList` with the given *list_id*, or ``None``."""
        return self._lists.get(list_id)

    # ------------------------------------------------------------------
    # Sharing
    # ------------------------------------------------------------------

    def create_invite_token(self, list_id: str) -> str:
        """Generate a one-time invite token for a list and return it."""
        if list_id not in self._lists:
            raise ValueError(f"Unknown list id: {list_id!r}")
        token = secrets.token_urlsafe(32)
        self._invite_tokens[token] = list_id
        return token

    def share_list_with_email(self, list_id: str, email: str) -> str:
        """
        Share a list with *email*.

        Returns an invite token that the invitee can use to join the list.
        If the invitee is not yet registered, a pending invite is also stored
        so that calling ``register_user`` with that e-mail address will
        automatically add them to the list.
        """
        if list_id not in self._lists:
            raise ValueError(f"Unknown list id: {list_id!r}")
        # Store a pending invite so that registration auto-joins the list.
        self._pending_invites[email.lower()] = list_id
        # Also create a token the invitee can present upon registration or later.
        token = self.create_invite_token(list_id)
        return token

    # ------------------------------------------------------------------
    # User registration with auto-join
    # ------------------------------------------------------------------

    def register_user(
        self,
        user_id: str,
        email: str,
        invite_token: Optional[str] = None,
    ) -> Optional[ClassList]:
        """
        Register a new user and automatically join any shared list they were invited to.

        The method checks two sources in order:
        1. A **pending invite** stored against the user's e-mail address
           (set when ``share_list_with_email`` was called before the user registered).
        2. An explicit **invite token** supplied directly by the caller.

        Returns the :class:`ClassList` the user was added to, or ``None`` if no
        invitation was found.
        """
        joined_list: Optional[ClassList] = None

        # 1. Process a pending e-mail invite (created before the user registered).
        normalized_email = email.lower()
        if normalized_email in self._pending_invites:
            list_id = self._pending_invites.pop(normalized_email)
            cls_list = self._lists.get(list_id)
            if cls_list is not None:
                cls_list.add_member(user_id)
                joined_list = cls_list

        # 2. Process an explicit invite token if one was provided.
        if invite_token is not None and invite_token in self._invite_tokens:
            list_id = self._invite_tokens.pop(invite_token)
            cls_list = self._lists.get(list_id)
            if cls_list is not None:
                cls_list.add_member(user_id)
                if joined_list is None:
                    joined_list = cls_list

        return joined_list

    # ------------------------------------------------------------------
    # Join via token (for already-registered users)
    # ------------------------------------------------------------------

    def join_list_with_token(self, user_id: str, invite_token: str) -> Optional[ClassList]:
        """
        Add *user_id* to the list associated with *invite_token*.

        Returns the joined :class:`ClassList`, or ``None`` if the token is invalid.
        The token is consumed and cannot be reused.
        """
        if invite_token not in self._invite_tokens:
            return None
        list_id = self._invite_tokens.pop(invite_token)
        cls_list = self._lists.get(list_id)
        if cls_list is None:
            return None
        cls_list.add_member(user_id)
        return cls_list
