import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { Auth } from '../models'
import API from '../api';


const initialState: Auth = { token: null, refreshToken: null, status: "" };

export const loginUser = createAsyncThunk('auth/loginUser',
    async (args: {
        email: string,
        password: string;
    }) => {
        const response = await API.post(`/user/token/`, args)
        return response.data
    })

export const registerUser = createAsyncThunk('auth/registerUser',
    async (args: {
        email: string,
        username: string;
        password: string;
    }) => {
        const response = await API.post(`/user/register`, args)
        return response.data
    })

const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setAccessTokens(
            state: Auth,
            action: PayloadAction<{ token: string; }>
        ) {
            state.token = action.payload.token;
        },
        logoutUser(state: Auth) {
            state.refreshToken = null;
            state.token = null;
        },
    },
    extraReducers(builder) {
        builder
            .addCase(loginUser.fulfilled, (state, action) => {
                const { access, refresh } = action.payload;
                state.token = access;
                state.refreshToken = refresh;
                state.status = "login successful";
            })
            .addCase(loginUser.rejected, (state, action) => {
                state.status = "login unsuccessful";
            })
            .addCase(registerUser.fulfilled, (state, action) => {
                const { email, username, password } = action.payload;
                const args = {
                    email,
                    password
                }
                loginUser(args)
            })
            .addCase(registerUser.rejected, (state, action) => {
                state.status = "registration rejected";
            })
    },
});

export const { logoutUser, setAccessTokens } = authSlice.actions

export default authSlice.reducer
