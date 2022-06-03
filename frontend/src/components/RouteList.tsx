import React, { useEffect, useRef, useState, Dispatch } from "react";
import { useAppSelector, useAppDispatch } from '../hooks'
import { selectAgency } from "../redux/features/agency";
import { fetchRoutes, idleRoutes, selectRoute, fetchRouteBBox, clearBBox } from "../redux/features/route";
import { Agency, Route } from '../redux/models'
import RouteDetail from "./RouteDetail";
import Button from '@mui/material/Button';


let RouteList = () => {

    const routes = useAppSelector(state => state.route.routes)
    const routesStatus = useAppSelector(state => state.route.status)
    const selectedRoute = useAppSelector(state => state.route.selectedRoute)
    const selectedAgency = useAppSelector(state => state.agency.selectedAgency)
    const dispatch = useAppDispatch()

    const deselectAgency = (agency: Agency | null) => {
        dispatch(selectAgency(agency))
        dispatch(idleRoutes())
        dispatch(selectRoute(null))
        dispatch(clearBBox())
    }

    const doSelectRoute = (route: Route) => {
        dispatch(selectRoute(route))
        dispatch(fetchRouteBBox(route.id))
    }

    const renderedRoutes = routes.map(a => {
        if (a.id === selectedRoute?.id) {
            return (<RouteDetail />)
        }
        else {
            return (
                <div className="route-container" key={a.id}>
                    <h3>{a.route_long_name}</h3>
                    <h3>{a.route_id}</h3>
                    <p className="route-content">{a.route_url.substring(0, 100)}</p>
                    <Button variant="outlined" onClick={() => doSelectRoute(a)}>Route Detail</Button>
                </div>
            )
        }
    })

    useEffect(() => {
        if (routesStatus === 'idle' && selectedAgency) {
            dispatch(fetchRoutes(selectedAgency.id))
        }
    }, [routesStatus, dispatch])

    return (
        <React.Fragment>
            <div className="sidebar-list-header">
                <Button variant="outlined" onClick={() => deselectAgency(null)}>Back to Agencies</Button>
            </div>

            <div id="route-list">
                {routesStatus === 'loading' ?
                    "loading..."
                    : routesStatus === 'succeeded' ?
                        renderedRoutes
                        : "error"
                }

            </div>
        </React.Fragment>
    );

}

export default RouteList;