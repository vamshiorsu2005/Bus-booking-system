import json
import datetime
from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_service
from app.repositories.trip import trip_repository
from app.schemas.trip import TripSearchResponse
from app.schemas.bus import BusOut, BusTypeOut
from app.schemas.route import RouteOut, CityOut, RouteStopOut, StopOut


class SearchService:
    def _get_cache_key(
        self,
        source_city_id: Any,
        destination_city_id: Any,
        journey_date: datetime.date
    ) -> str:
        return f"search:{source_city_id}:{destination_city_id}:{journey_date}"

    async def search_trips(
        self,
        db: AsyncSession,
        source_city_id: Any,
        destination_city_id: Any,
        journey_date: datetime.date,
        ac_only: Optional[bool] = None,
        seat_type: Optional[str] = None,
        bus_type_id: Optional[Any] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        bypass_cache: bool = False
    ) -> List[TripSearchResponse]:
        """
        Search for available trips between source and destination on a journey date.
        Uses Redis cache for raw search results unless bypass_cache is requested.
        """
        cache_key = self._get_cache_key(source_city_id, destination_city_id, journey_date)

        cached_data = None
        if not bypass_cache:
            try:
                cached_data = await redis_service.client.get(cache_key)
            except Exception:
                # Redis down should not block search (fallback to DB)
                pass

        if cached_data:
            # Parse list from cache
            try:
                raw_list = json.loads(cached_data)
                # Map back to schemas
                all_trips = [TripSearchResponse.model_validate(item) for item in raw_list]
            except Exception:
                # Fallback to DB if parsing fails
                all_trips = await self._fetch_and_cache_trips(db, source_city_id, destination_city_id, journey_date, cache_key)
        else:
            all_trips = await self._fetch_and_cache_trips(db, source_city_id, destination_city_id, journey_date, cache_key)

        # Apply filters in Python to the cached or retrieved search results
        filtered_trips = []
        for trip in all_trips:
            if ac_only is not None and trip.bus.bus_type.is_ac != ac_only:
                continue
            if seat_type and trip.bus.bus_type.seat_type != seat_type:
                continue
            if bus_type_id and trip.bus.bus_type.id != bus_type_id:
                continue
            if price_min is not None and float(trip.final_price) < price_min:
                continue
            if price_max is not None and float(trip.final_price) > price_max:
                continue
            filtered_trips.append(trip)

        return filtered_trips

    async def _fetch_and_cache_trips(
        self,
        db: AsyncSession,
        source_city_id: Any,
        destination_city_id: Any,
        journey_date: datetime.date,
        cache_key: str
    ) -> List[TripSearchResponse]:
        """Fetch trip records from DB and write to Redis cache."""
        trips = await trip_repository.search_trips(
            db,
            source_city_id=source_city_id,
            destination_city_id=destination_city_id,
            journey_date=journey_date
        )

        results = []
        for trip in trips:
            # Count available seats
            available_seats = sum(1 for s in trip.seat_inventories if s.status == "Available")
            final_price = trip.schedule.base_price * trip.price_modifier

            # Convert stops
            stops_out = []
            for rs in trip.schedule.route.route_stops:
                stops_out.append(
                    RouteStopOut(
                        id=rs.id,
                        route_id=rs.route_id,
                        stop=StopOut.model_validate(rs.stop),
                        sequence=rs.sequence,
                        distance_from_source=rs.distance_from_source,
                        time_from_source_mins=rs.time_from_source_mins
                    )
                )

            # Sort stops by sequence
            stops_out.sort(key=lambda x: x.sequence)

            route_out = RouteOut(
                id=trip.schedule.route.id,
                source_city=CityOut.model_validate(trip.schedule.route.source_city),
                destination_city=CityOut.model_validate(trip.schedule.route.destination_city),
                distance_km=trip.schedule.route.distance_km,
                duration_minutes=trip.schedule.route.duration_minutes,
                route_stops=stops_out
            )

            bus_out = BusOut(
                id=trip.schedule.bus.id,
                operator_id=trip.schedule.bus.operator_id,
                name=trip.schedule.bus.name,
                registration_number=trip.schedule.bus.registration_number,
                amenities=trip.schedule.bus.amenities,
                is_active=trip.schedule.bus.is_active,
                bus_type=BusTypeOut.model_validate(trip.schedule.bus.bus_type)
            )

            res = TripSearchResponse(
                trip_id=trip.id,
                journey_date=trip.journey_date,
                departure_time=trip.departure_time,
                arrival_time=trip.arrival_time,
                base_price=trip.schedule.base_price,
                final_price=final_price,
                status=trip.status,
                bus=bus_out,
                route=route_out,
                available_seats=available_seats
            )
            results.append(res)

        # Cache results in Redis (expiry: 60 seconds)
        try:
            # Dump list to JSON (using dict representation)
            data_to_cache = [r.model_dump(mode="json") for r in results]
            await redis_service.client.setex(
                cache_key,
                60,  # 60 seconds TTL
                json.dumps(data_to_cache)
            )
        except Exception:
            # Redis failures should not impact database queries
            pass

        return results


search_service = SearchService()
