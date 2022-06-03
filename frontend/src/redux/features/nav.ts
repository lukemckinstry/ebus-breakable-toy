import { createSlice } from '@reduxjs/toolkit'


interface NavState {
    showLoginModal: boolean,
}

// Define the initial state using that type
const initialState: NavState = {
    showLoginModal: false,
}



export const navSlice = createSlice({
    name: 'nav',
    // `createSlice` will infer the state type from the `initialState` argument
    initialState,
    reducers: {
        hideNavModal: (state) => {
            state.showLoginModal = false
        },
        showNavModal: (state) => {
            state.showLoginModal = true
        },
    }
})

export const { hideNavModal, showNavModal } = navSlice.actions

export default navSlice.reducer


// export default countSlice.reducer