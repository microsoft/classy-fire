# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest

from classy_fire.sharing import ClassList, ListRegistry


# ---------------------------------------------------------------------------
# ClassList unit tests
# ---------------------------------------------------------------------------

class TestClassList:
    def test_owner_is_initial_member(self):
        cls_list = ClassList("Fruits", ["Apple", "Banana"], owner="alice")
        assert cls_list.is_member("alice")

    def test_add_member(self):
        cls_list = ClassList("Fruits", ["Apple", "Banana"], owner="alice")
        cls_list.add_member("bob")
        assert cls_list.is_member("bob")

    def test_non_member(self):
        cls_list = ClassList("Fruits", ["Apple", "Banana"], owner="alice")
        assert not cls_list.is_member("charlie")

    def test_class_names_preserved(self):
        names = ["Cat", "Dog", "Bird"]
        cls_list = ClassList("Animals", names, owner="alice")
        assert cls_list.class_names == names

    def test_unique_ids(self):
        a = ClassList("A", ["X"], owner="u1")
        b = ClassList("B", ["Y"], owner="u2")
        assert a.id != b.id


# ---------------------------------------------------------------------------
# ListRegistry unit tests
# ---------------------------------------------------------------------------

class TestListRegistry:
    def setup_method(self):
        self.registry = ListRegistry()
        self.cls_list = self.registry.create_list(
            "Fruits", ["Apple", "Banana", "Cherry"], owner="alice"
        )

    def test_create_list_returns_class_list(self):
        assert isinstance(self.cls_list, ClassList)
        assert self.cls_list.name == "Fruits"
        assert self.cls_list.owner == "alice"

    def test_get_list(self):
        retrieved = self.registry.get_list(self.cls_list.id)
        assert retrieved is self.cls_list

    def test_get_list_unknown_id_returns_none(self):
        assert self.registry.get_list("nonexistent") is None

    def test_create_invite_token_returns_string(self):
        token = self.registry.create_invite_token(self.cls_list.id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_invite_token_unknown_list_raises(self):
        with pytest.raises(ValueError):
            self.registry.create_invite_token("nonexistent")

    def test_join_list_with_valid_token(self):
        token = self.registry.create_invite_token(self.cls_list.id)
        result = self.registry.join_list_with_token("bob", token)
        assert result is self.cls_list
        assert self.cls_list.is_member("bob")

    def test_join_list_with_invalid_token_returns_none(self):
        result = self.registry.join_list_with_token("bob", "bad-token")
        assert result is None

    def test_invite_token_is_consumed_after_use(self):
        token = self.registry.create_invite_token(self.cls_list.id)
        self.registry.join_list_with_token("bob", token)
        # Token should be gone now; second use returns None
        result = self.registry.join_list_with_token("charlie", token)
        assert result is None


# ---------------------------------------------------------------------------
# share_list_with_email tests
# ---------------------------------------------------------------------------

class TestShareListWithEmail:
    def setup_method(self):
        self.registry = ListRegistry()
        self.cls_list = self.registry.create_list(
            "Fruits", ["Apple", "Banana"], owner="alice"
        )

    def test_returns_invite_token(self):
        token = self.registry.share_list_with_email(self.cls_list.id, "bob@example.com")
        assert isinstance(token, str) and len(token) > 0

    def test_unknown_list_raises(self):
        with pytest.raises(ValueError):
            self.registry.share_list_with_email("nonexistent", "bob@example.com")

    def test_token_can_be_used_to_join(self):
        token = self.registry.share_list_with_email(self.cls_list.id, "bob@example.com")
        result = self.registry.join_list_with_token("bob", token)
        assert result is self.cls_list
        assert self.cls_list.is_member("bob")


# ---------------------------------------------------------------------------
# Auto-join on registration (the core fix)
# ---------------------------------------------------------------------------

class TestRegisterUserAutoJoin:
    """
    Tests for the fixed flow: when a list is shared with an e-mail address and
    the recipient registers afterwards, they are automatically added to the list.
    """

    def setup_method(self):
        self.registry = ListRegistry()
        self.cls_list = self.registry.create_list(
            "Fruits", ["Apple", "Banana", "Cherry"], owner="alice"
        )

    def test_auto_join_on_registration_via_email(self):
        """Core fix: user receives email invite *before* registering, then registers."""
        self.registry.share_list_with_email(self.cls_list.id, "bob@example.com")

        # Bob registers – should be auto-joined
        joined = self.registry.register_user("bob", "bob@example.com")

        assert joined is self.cls_list
        assert self.cls_list.is_member("bob")

    def test_auto_join_email_is_case_insensitive(self):
        """E-mail comparison must be case-insensitive."""
        self.registry.share_list_with_email(self.cls_list.id, "Bob@Example.COM")

        joined = self.registry.register_user("bob", "bob@example.com")

        assert joined is self.cls_list
        assert self.cls_list.is_member("bob")

    def test_auto_join_clears_pending_invite(self):
        """Pending invite should be consumed so a second registration doesn't re-join."""
        self.registry.share_list_with_email(self.cls_list.id, "bob@example.com")
        self.registry.register_user("bob", "bob@example.com")

        # Second registration with same email finds no pending invite
        joined = self.registry.register_user("bob2", "bob@example.com")
        assert joined is None

    def test_register_without_invite_returns_none(self):
        """A user with no pending invite or token gets None from register_user."""
        joined = self.registry.register_user("charlie", "charlie@example.com")
        assert joined is None
        assert not self.cls_list.is_member("charlie")

    def test_auto_join_via_invite_token_on_registration(self):
        """User can also supply an invite token explicitly during registration."""
        token = self.registry.create_invite_token(self.cls_list.id)

        joined = self.registry.register_user("dave", "dave@example.com", invite_token=token)

        assert joined is self.cls_list
        assert self.cls_list.is_member("dave")

    def test_invite_token_consumed_on_registration(self):
        """Token supplied during registration should be consumed."""
        token = self.registry.create_invite_token(self.cls_list.id)
        self.registry.register_user("dave", "dave@example.com", invite_token=token)

        # Token no longer valid
        result = self.registry.join_list_with_token("eve", token)
        assert result is None

    def test_email_invite_and_token_both_processed(self):
        """If a user has both a pending e-mail invite and a token, both are processed."""
        token = self.registry.create_invite_token(self.cls_list.id)
        self.registry.share_list_with_email(self.cls_list.id, "frank@example.com")

        joined = self.registry.register_user(
            "frank", "frank@example.com", invite_token=token
        )

        # Should be a member (at least one invite succeeded)
        assert self.cls_list.is_member("frank")
        assert joined is self.cls_list

    def test_owner_is_not_affected_by_registration_flow(self):
        """The owner is already a member and should remain so."""
        assert self.cls_list.is_member("alice")
