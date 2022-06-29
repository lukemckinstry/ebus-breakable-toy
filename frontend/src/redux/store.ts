import { configureStore } from '@reduxjs/toolkit'
import { combineReducers } from 'redux'
import {
    persistStore,
    persistReducer,
} from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import countReducer from './features/count'
import agencyReducer from './features/agency'
import authReducer from './features/auth'
import routeReducer from './features/route'
import navReducer from './features/nav'

const reducers = combineReducers({
    count: countReducer,
    agency: agencyReducer,
    route: routeReducer,
    auth: authReducer,
    nav: navReducer,
});

const persistConfig = {
    key: 'root',
    version: 1,
    storage,
}

const persistedReducer = persistReducer(persistConfig, reducers)

export const store = configureStore({
    reducer: persistedReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                //ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
            },
        }),
})

export const persistor = persistStore(store);
// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
// Inferred type: {count: CountState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch