import pytest
import datetime
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.bus import Bus, BusType, SeatLayout
from app.models.route import Route, State, City, Stop
from app.models.trip import Schedule, Trip
from app.core.redis import redis_service


@pytest.mark.asyncio

async def test_operator_and_search_flow(client: AsyncClient, db: AsyncSession):
    # 1. Register operator & get token
    operator_payload = {
        "email": "op_flow@example.com",
        "password": "testpassword123",
        "full_name": "Flow Operator",
        "role": "operator"
    }
    reg_res = await client.post("/api/v1/auth/register", json=operator_payload)
    assert reg_res.status_code == 201

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "op_flow@example.com",
        "password": "testpassword123"
    })
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 2. Create Bus Type & Seat Layout
    bus_type_payload = {
        "bus_type_in": {
            "name": "Luxury Sleeper AC",
            "is_ac": True,
            "seat_type": "Sleeper",
            "capacity": 2
        },
        "layouts": [
            {"seat_number": "L1", "row": 1, "col": 1, "seat_tier": "Lower", "is_sleeper": True},
            {"seat_number": "L2", "row": 1, "col": 2, "seat_tier": "Lower", "is_sleeper": True}
        ]
    }
    bus_type_res = await client.post("/api/v1/operator/bus-types", json=bus_type_payload, headers=headers)
    assert bus_type_res.status_code == 201
    bus_type_data = bus_type_res.json()
    bus_type_id = bus_type_data["id"]

    # 3. Create Bus
    bus_payload = {
        "name": "Humsafar Travels Benz",
        "registration_number": "MH-12-Q-9999",
        "amenities": {"wifi": True, "water": True, "blanket": True},
        "is_active": True,
        "bus_type_id": bus_type_id
    }
    bus_res = await client.post("/api/v1/operator/buses", json=bus_payload, headers=headers)
    assert bus_res.status_code == 201
    bus_data = bus_res.json()
    bus_id = bus_data["id"]

    # 4. Set up Geography (State & City & Stop)
    # Insert States and Cities directly in DB for testing
    state_ka = State(name="Karnataka", code="KA")
    db.add(state_ka)
    await db.flush()

    city_blr = City(name="Bengaluru", code="BLR", state_id=state_ka.id)
    city_mys = City(name="Mysuru", code="MYS", state_id=state_ka.id)
    db.add_all([city_blr, city_mys])
    await db.flush()

    stop_blr = Stop(name="Majestic", latitude=12.9778, longitude=77.5721, city_id=city_blr.id)
    stop_mys = Stop(name="Suburban Stand", latitude=12.3086, longitude=76.6554, city_id=city_mys.id)
    db.add_all([stop_blr, stop_mys])
    await db.flush()

    # 5. Create Route via API
    route_payload = {
        "source_city_id": str(city_blr.id),
        "destination_city_id": str(city_mys.id),
        "distance_km": 145.50,
        "duration_minutes": 180,
        "stops": [
            {
                "stop_id": str(stop_blr.id),
                "sequence": 1,
                "distance_from_source": 0.0,
                "time_from_source_mins": 0
            },
            {
                "stop_id": str(stop_mys.id),
                "sequence": 2,
                "distance_from_source": 145.50,
                "time_from_source_mins": 180
            }
        ]
    }
    route_res = await client.post("/api/v1/operator/routes", json=route_payload, headers=headers)
    assert route_res.status_code == 201
    route_data = route_res.json()
    route_id = route_data["id"]

    # 6. Create Schedule
    schedule_payload = {
        "bus_id": bus_id,
        "route_id": route_id,
        "departure_time": "08:00:00",
        "arrival_time": "11:00:00",
        "days_of_week": 127,
        "base_price": 500.00
    }
    schedule_res = await client.post("/api/v1/operator/schedules", json=schedule_payload, headers=headers)
    assert schedule_res.status_code == 201
    schedule_data = schedule_res.json()
    schedule_id = schedule_data["id"]

    # 7. Generate Trip
    journey_date = (datetime.date.today() + datetime.timedelta(days=1))
    trip_payload = {
        "schedule_id": schedule_id,
        "journey_date": str(journey_date),
        "departure_time": f"{journey_date}T08:00:00",
        "arrival_time": f"{journey_date}T11:00:00",
        "price_modifier": 1.10,
        "status": "Scheduled"
    }
    trip_res = await client.post("/api/v1/operator/trips", json=trip_payload, headers=headers)
    assert trip_res.status_code == 201
    trip_data = trip_res.json()
    trip_id = trip_data["id"]

    # 8. Search Trip
    search_query = f"/api/v1/search?source_city_id={city_blr.id}&destination_city_id={city_mys.id}&journey_date={journey_date}"
    search_res = await client.get(search_query)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data) == 1
    assert search_data[0]["trip_id"] == trip_id
    assert search_data[0]["final_price"] == 550.0  # 500 * 1.10 = 550
    assert search_data[0]["available_seats"] == 2

    # 9. Verify Caching in Redis
    cache_key = f"search:{city_blr.id}:{city_mys.id}:{journey_date}"
    cached = await redis_service.client.get(cache_key)
    assert cached is not None

    # Check search with AC filter
    ac_res = await client.get(f"{search_query}&ac_only=true")
    assert len(ac_res.json()) == 1

    # Check search with non-AC filter (should return 0 results)
    non_ac_res = await client.get(f"{search_query}&ac_only=false")
    assert len(non_ac_res.json()) == 0
