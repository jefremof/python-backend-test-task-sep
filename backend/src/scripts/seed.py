import asyncio
import random
from typing import List

from src.scripts.factories import (
    BuildingFactory,
    ActivityFactory,
    OrganizationFactory,
    OrganizationPhoneFactory,
)
from src.database import AsyncSessionLocal
from src.models import Building, Activity, Organization, OrganizationPhones


async def create_activities(
    session,
    n_roots: int,
    children_per_root: int,
    grandchildren_per_child: int,
) -> List[Activity]:

    roots: List[Activity] = ActivityFactory.build_batch(n_roots)
    session.add_all(roots)
    await session.flush()

    level2: List[Activity] = []
    for root in roots:
        for _ in range(children_per_root):
            a = ActivityFactory.build()
            a.parent = root
            level2.append(a)
    session.add_all(level2)
    await session.flush()

    level3: List[Activity] = []
    for parent in level2:
        for _ in range(grandchildren_per_child):
            a = ActivityFactory.build()
            a.parent = parent
            level3.append(a)
    session.add_all(level3)
    await session.flush()

    return roots + level2 + level3


async def create_buildings(session, n_buildings: int) -> List[Building]:
    buildings: List[Building] = BuildingFactory.build_batch(n_buildings)
    session.add_all(buildings)
    await session.flush()
    return buildings


async def create_organizations(
    session,
    buildings: List[Building],
    activities: List[Activity],
    n_orgs: int,
    max_phones_per_org: int,
    batch_size: int,
):
    created = 0
    while created < n_orgs:
        batch_count = min(batch_size, n_orgs - created)
        batch: List[Organization] = []
        for _ in range(batch_count):
            org = OrganizationFactory.build()
            org.building = random.choice(buildings)

            phone_count = random.randint(1, max_phones_per_org)
            phones: List[OrganizationPhones] = []
            for _ in range(phone_count):
                p = OrganizationPhoneFactory.build()
                p.organization = org
                phones.append(p)
            org.phones = phones

            k = min(5, len(activities))
            pick_n = random.randint(1, k)
            org.activities = random.sample(activities, k=pick_n)

            batch.append(org)

        session.add_all(batch)
        await session.commit()
        created += batch_count
        print(f"Committed {created}/{n_orgs} organizations")


async def seed(
    n_buildings: int,
    n_roots: int,
    children_per_root: int,
    grandchildren_per_child: int,
    n_orgs: int,
    max_phones_per_org: int,
    batch_size: int,
):
    async with AsyncSessionLocal() as session:
        print("Creating activities (3 levels)")
        activities = await create_activities(
            session,
            n_roots=n_roots,
            children_per_root=children_per_root,
            grandchildren_per_child=grandchildren_per_child,
        )
        print(f"Created {len(activities)} activities")

        print("Creating buildings...")
        buildings = await create_buildings(session, n_buildings=n_buildings)
        print(f"Created {len(buildings)} buildings")

        print("Creating organizations...")
        await create_organizations(
            session,
            buildings=buildings,
            activities=activities,
            n_orgs=n_orgs,
            max_phones_per_org=max_phones_per_org,
            batch_size=batch_size,
        )
        print("Seeding finished.")


if __name__ == "__main__":
    asyncio.run(
        seed(
            n_buildings=15,
            n_roots=4,
            children_per_root=3,
            grandchildren_per_child=2,
            n_orgs=200,
            max_phones_per_org=2,
            batch_size=50,
        )
    )
