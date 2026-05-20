from django.test import TestCase
import pytest

from extras.test_utils.old_factories.account import UserFactory
from extras.test_utils.old_factories.core import create_afghanistan
from hope.contrib.vision.fixtures import FundsCommitmentFactory
from hope.contrib.vision.models import (
    DownPayment,
    FundsCommitment,
    FundsCommitmentGroup,
    FundsCommitmentItem,
)

pytestmark = pytest.mark.django_db


class TestFundsCommitmentDBTrigger(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()

    def test_trigger_creates_rows(self) -> None:
        assert FundsCommitmentGroup.objects.count() == 0
        assert FundsCommitmentItem.objects.count() == 0

        FundsCommitmentFactory(funds_commitment_number="123")

        assert FundsCommitmentGroup.objects.count() == 1
        assert FundsCommitmentItem.objects.count() == 1

        FundsCommitmentFactory(funds_commitment_number="123")

        assert FundsCommitmentGroup.objects.count() == 1
        assert FundsCommitmentItem.objects.count() == 2

        FundsCommitmentFactory(funds_commitment_number="345")

        assert FundsCommitmentGroup.objects.count() == 2
        assert FundsCommitmentItem.objects.count() == 3

        fcg = FundsCommitmentGroup.objects.get(funds_commitment_number="123")
        assert fcg.funds_commitment_items.count() == 2

        fcg = FundsCommitmentGroup.objects.get(funds_commitment_number="345")
        assert fcg.funds_commitment_items.count() == 1


class TestStr(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()

    def test_funds_commitment_group_str(self) -> None:
        fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
        assert str(fcg) == "FC-001"

    def test_funds_commitment_item_str(self) -> None:
        fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
        fci = FundsCommitmentItem.objects.create(
            funds_commitment_group=fcg,
            rec_serial_number=12345,
            funds_commitment_item="001",
        )
        assert str(fci) == "FC-001 - 001"

    def test_funds_commitment_str(self) -> None:
        fc = FundsCommitment.objects.create(
            rec_serial_number=67890,
            funds_commitment_number="FC-002",
        )
        assert str(fc) == "FC-002"

    def test_down_payment_str(self) -> None:
        dp = DownPayment.objects.create(
            rec_serial_number=99999,
            business_area="BA01",
            down_payment_reference="DP-REF-001",
            document_type="DO",
            consumed_fc_number="FC-001",
            total_down_payment_amount_local=1000.00,
        )
        assert str(dp) == "99999"
