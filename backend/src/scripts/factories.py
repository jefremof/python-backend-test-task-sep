from __future__ import annotations
import factory
from faker import Faker

from src.models import Building, Organization, OrganizationPhones, Activity

fake = Faker()
Faker.seed(0)

class BuildingFactory(factory.Factory):
    class Meta:
        model = Building

    address = factory.Sequence(lambda n: f"Testcity, test St. {n}")
    latitude = factory.LazyFunction(lambda: float(fake.latitude()))
    longitude = factory.LazyFunction(lambda: float(fake.longitude()))

class ActivityFactory(factory.Factory):
    class Meta:
        model = Activity

    name = factory.Sequence(lambda n: f"Activity {n}")

class OrganizationPhoneFactory(factory.Factory):
    class Meta:
        model = OrganizationPhones

    number = factory.Sequence(lambda n: f"+79000{n:06d}")

class OrganizationFactory(factory.Factory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Organization {n}")