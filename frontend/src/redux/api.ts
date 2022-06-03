import axios from 'axios';
import { Store } from "@reduxjs/toolkit";
import { setAccessTokens, logoutUser } from './features/auth';


axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";
axios.defaults.withCredentials = true

const axiosService = axios.create({
    baseURL: ``
});

const setupInterceptors = (store: Store) => {
    axiosService.interceptors.request.use((config) => {
        const { token } = store.getState().auth;
        if (token !== null) {
            if (config.headers === undefined) {
                config.headers = {};
            }
            config.headers.Authorization = 'Bearer ' + token;
            // @ts-ignore
            console.debug('[Request]', config.baseURL + config.url, JSON.stringify(token));
        }
        return config;
    });
    axiosService.interceptors.response.use(
        (res) => {
            // @ts-ignore
            console.debug('[Response]', res.config.baseURL + res.config.url, res.status, res.data);
            return Promise.resolve(res);
        },
        (err) => {
            console.debug(
                '[Response]',
                err.config.baseURL + err.config.url,
                err.response.status,
                err.response.data
            );
            if (err.response && err.response.status === 401) {
                console.debug("here failed request 1")
                const failedRequest = err.config;
                const { refreshToken } = store.getState().auth;
                if (refreshToken !== null) {
                    return axios
                        .post('/user/token/refresh/', {
                            refresh: refreshToken,
                        })
                        .then((resp) => {
                            const { access } = resp.data;
                            store.dispatch(setAccessTokens({ token: access }))
                            return axiosService(failedRequest);
                        })
                        .catch((err) => {
                            if (err.response && err.response.status === 401) {
                                store.dispatch(logoutUser());
                            }
                        });
                }
            }
            return Promise.reject(err);
        }
    );
};


export { setupInterceptors };

export default axiosService;