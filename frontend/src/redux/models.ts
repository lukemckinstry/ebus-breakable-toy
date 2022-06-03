
export interface Agency {
    id: string,
    agency_id: string,
    agency_name: string,
    agency_url: string,
    agency_timezone: string,
    agency_phone: string,
    agency_fare_url: string,
    agency_email: string,
    num_vehicles: number,
    num_zero_emission_vehicles: number
}

export interface Route {
    id: string,
    route_id: string,
    agency: string,
    route_short_name: string,
    route_long_name: string,
    route_desc: string,
    route_type: string,
    route_url: string,
    route_color: string,
    route_distance: number,
    trips_monday: number,
    trips_tuesday: number,
    trips_wednesday: number,
    trips_thursday: number,
    trips_friday: number,
    trips_saturday: number,
    trips_sunday: number,
    zev_charging_infrastructure: boolean,
    zev_notes: string,
    pct_zev_service: number,
    num_zev: number
}

export interface Auth {
    token: string | null,
    refreshToken: string | null,
    status: string,
}