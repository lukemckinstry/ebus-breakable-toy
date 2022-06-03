import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../store'
import { Agency } from '../models'
import API from '../api';

interface AgencyState {
    agencies: Agency[],
    selectedAgency: Agency | null,
    status: 'idle' | 'loading' | 'succeeded' | 'failed',
    error: string | null
}

// Define the initial state using that type
const initialState: AgencyState = {
    agencies: [
        {
            id: 'test_id1',
            agency_id: 'test_agency1',
            agency_name: 'test_agency1',
            agency_url: 'test_agency1',
            agency_timezone: 'test_agency1',
            agency_phone: 'test_agency1',
            agency_fare_url: 'test_agency1',
            agency_email: 'test_agency1',
            num_vehicles: 0,
            num_zero_emission_vehicles: 0
        },
        {
            id: 'test_id2',
            agency_id: 'test_agency2',
            agency_name: 'test_agency2',
            agency_url: 'test_agency2',
            agency_timezone: 'test_agency2',
            agency_phone: 'test_agency2',
            agency_fare_url: 'test_agency2',
            agency_email: 'test_agency2',
            num_vehicles: 0,
            num_zero_emission_vehicles: 0
        },
    ],
    selectedAgency: null,
    status: 'idle',
    error: null
}

export const fetchAgencies = createAsyncThunk('agencies/fetchAgencies', async () => {
    const response = await API.get('agency/')
    return response.data
})


export const agencySlice = createSlice({
    name: 'agency',
    // `createSlice` will infer the state type from the `initialState` argument
    initialState,
    reducers: {
        selectAgency(state, action: PayloadAction<Agency | null>) {
            state.selectedAgency = action.payload
        },
    },
    extraReducers(builder) {
        builder
            .addCase(fetchAgencies.pending, (state, action) => {
                state.status = 'loading'
            })
            .addCase(fetchAgencies.fulfilled, (state, action) => {
                state.status = 'succeeded'
                // Add any fetched agencies to the array
                state.agencies = action.payload
            })
            .addCase(fetchAgencies.rejected, (state, action) => {
                state.status = 'failed'
                state.error = action.error.message || null
            })
    }
})

//export const { increment, decrement, incrementByAmount } = counterSlice.actions

// Other code such as selectors can use the imported `RootState` type
//export const selectAgency = (state: RootState) => state.agency

export const { selectAgency } = agencySlice.actions

export default agencySlice.reducer