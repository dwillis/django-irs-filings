from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.core.management import call_command
from django.db.models import Sum, Count, Q
from django.utils import timezone
from irs.models import F8872, Contribution, Expenditure, Committee


class IRSFilingsTest(TestCase):
    """Test suite for loading IRS filings data."""

    @classmethod
    def setUpClass(cls):
        """Setup the test database by loading a subset of a real filing."""
        super().setUpClass()
        call_command('loadIRS', test=True, verbose=False)

    def test_load_command(self):
        """Check if all the models were loaded correctly."""
        self.assertEqual(F8872.objects.count(), 65)
        self.assertEqual(Contribution.objects.count(), 5911)
        self.assertEqual(Expenditure.objects.count(), 5068)
        self.assertEqual(Committee.objects.count(), 49)

    def test_committee(self):
        """Check if committees are associated with their filings correctly."""
        committee = Committee.objects.get(EIN='751954937')
        self.assertEqual(
            committee.name,
            'GARDERE WYNNE SEWELL L L P CAMPAIGN FUND')
        self.assertEqual(committee.filings.count(), 3)

    def test_contributions(self):
        """Check if contributions and their totals are loaded correctly."""
        filing = F8872.objects.get(form_id_number='9637673')
        contributions_list = filing.contributions.values_list(
            'contribution_amount',
            flat=True)
        sum_contributions = sum(a for a in contributions_list)
        self.assertEqual(sum_contributions, filing.schedule_a_total)

    def test_amendments(self):
        """Check if amendments are being resolved correctly."""
        filing = F8872.objects.get(form_id_number='9637689')
        self.assertEqual(
            filing.amends.first().form_id_number,
            '9637644')
        amended_filing = F8872.objects.get(form_id_number='9637644')
        self.assertTrue(amended_filing.is_amended)
        self.assertEqual(
            amended_filing.amended_by.form_id_number,
            '9637689')


class ModelTests(TestCase):
    """Test model methods and properties."""

    def setUp(self):
        """Create test data."""
        self.committee = Committee.objects.create(
            EIN='123456789',
            name='Test Committee')

        self.filing = F8872.objects.create(
            committee=self.committee,
            record_type='2',
            form_type=8872,
            form_id_number='TEST001',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Test Committee',
            EIN='123456789',
            schedule_a_total=Decimal('10000.00'),
            schedule_b_total=Decimal('8000.00'),
            insert_datetime=timezone.now()
        )

    def test_committee_str(self):
        """Test Committee __str__ method."""
        self.assertEqual(str(self.committee), 'Test Committee')

    def test_filing_str(self):
        """Test F8872 __str__ method."""
        self.assertEqual(str(self.filing), 'TEST001')

    def test_contribution_str_with_name(self):
        """Test Contribution __str__ method with contributor name."""
        contribution = Contribution.objects.create(
            record_type='A',
            form_id_number='TEST001',
            schedule_a_id='A001',
            organization_name='Test Committee',
            EIN='123456789',
            contributor_name='John Doe',
            contribution_amount=Decimal('1000.00'),
            filing=self.filing,
            committee=self.committee
        )
        self.assertEqual(str(contribution), 'John Doe')

    def test_contribution_str_without_name(self):
        """Test Contribution __str__ method without contributor name."""
        contribution = Contribution.objects.create(
            record_type='A',
            form_id_number='TEST001',
            schedule_a_id='A002',
            organization_name='Test Committee',
            EIN='123456789',
            contribution_amount=Decimal('500.00'),
            filing=self.filing,
            committee=self.committee
        )
        self.assertEqual(str(contribution), '')

    def test_expenditure_str_with_name(self):
        """Test Expenditure __str__ method with recipient name."""
        expenditure = Expenditure.objects.create(
            record_type='B',
            form_id_number='TEST001',
            schedule_b_id='B001',
            organization_name='Test Committee',
            EIN='123456789',
            recipient_name='Consulting Firm',
            expenditure_amount=Decimal('2000.00'),
            filing=self.filing,
            committee=self.committee
        )
        self.assertEqual(str(expenditure), 'Consulting Firm')

    def test_expenditure_str_without_name(self):
        """Test Expenditure __str__ method without recipient name."""
        expenditure = Expenditure.objects.create(
            record_type='B',
            form_id_number='TEST001',
            schedule_b_id='B002',
            organization_name='Test Committee',
            EIN='123456789',
            expenditure_amount=Decimal('300.00'),
            filing=self.filing,
            committee=self.committee
        )
        self.assertEqual(str(expenditure), '')

    def test_filing_ordering(self):
        """Test that filings are ordered by end_date descending."""
        filing2 = F8872.objects.create(
            committee=self.committee,
            record_type='2',
            form_type=8872,
            form_id_number='TEST002',
            begin_date=date(2024, 4, 1),
            end_date=date(2024, 6, 30),
            organization_name='Test Committee',
            EIN='123456789',
            schedule_a_total=Decimal('5000.00'),
            schedule_b_total=Decimal('4000.00'),
            insert_datetime=timezone.now()
        )
        filings = list(F8872.objects.all())
        self.assertEqual(filings[0].form_id_number, 'TEST002')
        self.assertEqual(filings[1].form_id_number, 'TEST001')

    def test_committee_relationship(self):
        """Test committee foreign key relationships."""
        self.assertEqual(self.committee.filings.count(), 1)
        self.assertEqual(self.committee.filings.first(), self.filing)

    def test_filing_amendment_relationship(self):
        """Test filing amendment relationships."""
        amended_filing = F8872.objects.create(
            committee=self.committee,
            record_type='2',
            form_type=8872,
            form_id_number='TEST003',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Test Committee',
            EIN='123456789',
            schedule_a_total=Decimal('12000.00'),
            schedule_b_total=Decimal('9000.00'),
            insert_datetime=timezone.now(),
            is_amended=True,
            amended_by=self.filing
        )
        self.assertTrue(amended_filing.is_amended)
        self.assertEqual(amended_filing.amended_by, self.filing)
        self.assertEqual(self.filing.amends.first(), amended_filing)


class QueryTests(TestCase):
    """Test database queries and aggregations."""

    def setUp(self):
        """Create test data for queries."""
        self.committee1 = Committee.objects.create(
            EIN='111111111',
            name='Committee One')
        self.committee2 = Committee.objects.create(
            EIN='222222222',
            name='Committee Two')

        self.filing1 = F8872.objects.create(
            committee=self.committee1,
            record_type='2',
            form_type=8872,
            form_id_number='QUERY001',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Committee One',
            EIN='111111111',
            schedule_a_total=Decimal('10000.00'),
            schedule_b_total=Decimal('8000.00'),
            insert_datetime=timezone.now()
        )

        # Create contributions
        for i in range(5):
            Contribution.objects.create(
                record_type='A',
                form_id_number='QUERY001',
                schedule_a_id=f'A{i:03d}',
                organization_name='Committee One',
                EIN='111111111',
                contributor_name=f'Contributor {i}',
                contribution_amount=Decimal('1000.00'),
                contribution_date=date(2024, 1, 15),
                filing=self.filing1,
                committee=self.committee1
            )

    def test_contribution_aggregation(self):
        """Test aggregating contributions."""
        total = Contribution.objects.aggregate(
            total=Sum('contribution_amount'))['total']
        self.assertEqual(total, Decimal('5000.00'))

    def test_contribution_filtering(self):
        """Test filtering contributions."""
        contributions = Contribution.objects.filter(
            committee=self.committee1,
            contribution_date=date(2024, 1, 15)
        )
        self.assertEqual(contributions.count(), 5)

    def test_committee_with_multiple_filings(self):
        """Test querying committees with multiple filings."""
        F8872.objects.create(
            committee=self.committee1,
            record_type='2',
            form_type=8872,
            form_id_number='QUERY002',
            begin_date=date(2024, 4, 1),
            end_date=date(2024, 6, 30),
            organization_name='Committee One',
            EIN='111111111',
            schedule_a_total=Decimal('5000.00'),
            schedule_b_total=Decimal('4000.00'),
            insert_datetime=timezone.now()
        )
        self.assertEqual(self.committee1.filings.count(), 2)

    def test_amended_filings_query(self):
        """Test querying amended filings."""
        amended_count = F8872.objects.filter(is_amended=True).count()
        self.assertEqual(amended_count, 0)

        # Create an amended filing
        F8872.objects.create(
            committee=self.committee1,
            record_type='2',
            form_type=8872,
            form_id_number='QUERY003',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Committee One',
            EIN='111111111',
            schedule_a_total=Decimal('11000.00'),
            schedule_b_total=Decimal('8500.00'),
            insert_datetime=timezone.now(),
            is_amended=True,
            amended_by=self.filing1
        )
        amended_count = F8872.objects.filter(is_amended=True).count()
        self.assertEqual(amended_count, 1)


class EdgeCaseTests(TestCase):
    """Test edge cases and data validation."""

    def test_contribution_with_null_values(self):
        """Test contribution with null optional fields."""
        committee = Committee.objects.create(
            EIN='999999999',
            name='Edge Case Committee')
        filing = F8872.objects.create(
            committee=committee,
            record_type='2',
            form_type=8872,
            form_id_number='EDGE001',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Edge Case Committee',
            EIN='999999999',
            schedule_a_total=Decimal('0.00'),
            schedule_b_total=Decimal('0.00'),
            insert_datetime=timezone.now()
        )

        contribution = Contribution.objects.create(
            record_type='A',
            form_id_number='EDGE001',
            schedule_a_id='A001',
            organization_name='Edge Case Committee',
            EIN='999999999',
            filing=filing,
            committee=committee
        )
        self.assertIsNone(contribution.contributor_name)
        self.assertIsNone(contribution.contribution_amount)
        self.assertIsNone(contribution.contribution_date)

    def test_expenditure_with_null_values(self):
        """Test expenditure with null optional fields."""
        committee = Committee.objects.create(
            EIN='888888888',
            name='Another Committee')
        filing = F8872.objects.create(
            committee=committee,
            record_type='2',
            form_type=8872,
            form_id_number='EDGE002',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Another Committee',
            EIN='888888888',
            schedule_a_total=Decimal('0.00'),
            schedule_b_total=Decimal('0.00'),
            insert_datetime=timezone.now()
        )

        expenditure = Expenditure.objects.create(
            record_type='B',
            form_id_number='EDGE002',
            schedule_b_id='B001',
            organization_name='Another Committee',
            EIN='888888888',
            filing=filing,
            committee=committee
        )
        self.assertIsNone(expenditure.recipient_name)
        self.assertIsNone(expenditure.expenditure_amount)
        self.assertIsNone(expenditure.expenditure_date)

    def test_large_decimal_values(self):
        """Test handling of large monetary values."""
        committee = Committee.objects.create(
            EIN='777777777',
            name='Big Money Committee')
        filing = F8872.objects.create(
            committee=committee,
            record_type='2',
            form_type=8872,
            form_id_number='EDGE003',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Big Money Committee',
            EIN='777777777',
            schedule_a_total=Decimal('999999999999999.99'),
            schedule_b_total=Decimal('888888888888888.88'),
            insert_datetime=timezone.now()
        )
        self.assertEqual(filing.schedule_a_total, Decimal('999999999999999.99'))
        self.assertEqual(filing.schedule_b_total, Decimal('888888888888888.88'))

    def test_timezone_aware_datetimes(self):
        """Test that datetime fields are timezone-aware."""
        committee = Committee.objects.create(
            EIN='666666666',
            name='Timezone Test')
        now = timezone.now()
        filing = F8872.objects.create(
            committee=committee,
            record_type='2',
            form_type=8872,
            form_id_number='EDGE004',
            begin_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            organization_name='Timezone Test',
            EIN='666666666',
            schedule_a_total=Decimal('0.00'),
            schedule_b_total=Decimal('0.00'),
            insert_datetime=now
        )
        self.assertIsNotNone(filing.insert_datetime.tzinfo)
