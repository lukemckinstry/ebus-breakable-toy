import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../store'
import { Route } from '../models'
import API from '../api';


interface RouteState {
    routes: Route[],
    status: 'idle' | 'loading' | 'succeeded' | 'failed',
    selectedRoute: Route | null,
    selectedRouteBBox: number[],
    error: string | null
}

// Define the initial state using that type
const initialState: RouteState = {
    routes: [
        {
            id: 'route1',
            route_id: 'sample_id1',
            agency: 'agencyid1',
            route_short_name: 'rte1',
            route_long_name: 'route1',
            route_desc: 'route1',
            route_type: 'route1',
            route_url: 'route1',
            route_color: 'route1',
            route_distance: 0,
            trips_monday: 0,
            trips_tuesday: 0,
            trips_wednesday: 0,
            trips_thursday: 0,
            trips_friday: 0,
            trips_saturday: 0,
            trips_sunday: 0,
            zev_charging_infrastructure: true,
            zev_notes: "route1",
            pct_zev_service: 0,
            num_zev: 0
        },
        {
            id: 'route2',
            route_id: 'sample_id2',
            agency: 'agencyid2',
            route_short_name: 'rte2',
            route_long_name: 'route2',
            route_desc: 'route2',
            route_type: 'route2',
            route_url: 'route2',
            route_color: 'route2',
            route_distance: 0,
            trips_monday: 0,
            trips_tuesday: 0,
            trips_wednesday: 0,
            trips_thursday: 0,
            trips_friday: 0,
            trips_saturday: 0,
            trips_sunday: 0,
            zev_charging_infrastructure: true,
            zev_notes: "route2",
            pct_zev_service: 0,
            num_zev: 0
        },
    ],
    status: 'idle',
    selectedRoute: null,
    selectedRouteBBox: [],
    error: null
}

export const fetchRoutes = createAsyncThunk('routes/fetchRoutes', async (agency_id: string) => {
    const response = await API.get(`agency/${agency_id}/route`)
    return response.data
})

export const fetchRouteBBox = createAsyncThunk('routes/fetchRouteBBox', async (route_id: string) => {
    const response = await API.get(`route/bbox/${route_id}`)
    return response.data.bbox
})

export const updateRoute = createAsyncThunk(
    'routes/updateRoute',
    async (args: {
        route: Route;
        changes: Partial<Route>;
        updatedAt: ReturnType<typeof Date.prototype.toISOString>;
    }, { getState }) => {
        const { route, changes } = args;
        const obj = {
            ...route,
            ...changes,
        }
        const response = await API.put(`route/${route.id}/`, obj);
        return response.data
    }
);

export const routeSlice = createSlice({
    name: 'route',
    // `createSlice` will infer the state type from the `initialState` argument
    initialState,
    reducers: {
        idleRoutes: (state) => {
            state.status = 'idle'
        },
        selectRoute(state, action: PayloadAction<Route | null>) {
            state.selectedRoute = action.payload
        },
        clearBBox: (state) => {
            state.selectedRouteBBox = []
        },
    },
    extraReducers(builder) {
        builder
            .addCase(fetchRoutes.pending, (state, action) => {
                state.status = 'loading'
            })
            .addCase(fetchRoutes.fulfilled, (state, action) => {
                state.status = 'succeeded'
                // Add any fetched agencies to the array
                state.routes = action.payload
            })
            .addCase(fetchRoutes.rejected, (state, action) => {
                state.status = 'failed'
                state.error = action.error.message || null
            })
            .addCase(fetchRouteBBox.fulfilled, (state, action) => {
                // Set array to fetched route bbox
                state.selectedRouteBBox = action.payload
            })
            .addCase(updateRoute.pending, (state, action) => {
                const { route, changes } = action.meta.arg;
                let idx = state.routes.findIndex(r => r.id === route.id)
                state.routes[idx] = {
                    ...route,
                    ...changes,
                };
            })
            .addCase(updateRoute.fulfilled, (state, action) => {
                const { route } = action.meta.arg;
                let idx = state.routes.findIndex(r => r.id === route.id)
                state.routes[idx] = action.payload
            })
            .addCase(updateRoute.rejected, (state, action) => {
                const { route } = action.meta.arg;
                let idx = state.routes.findIndex(r => r.id === route.id)
                state.routes[idx] = route
            })
    }
})

//export const { increment, decrement, incrementByAmount } = counterSlice.actions

// Other code such as selectors can use the imported `RootState` type
export const selectRoutes = (state: RootState) => state.route.routes

export const { idleRoutes, selectRoute, clearBBox } = routeSlice.actions

export default routeSlice.reducer


// export default countSlice.reducer