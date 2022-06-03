import React, { useEffect, useRef, useState, Dispatch } from "react";
import { useAppSelector, useAppDispatch } from '../hooks'
import { fetchAgencies, selectAgency } from "../redux/features/agency";
import Button from '@mui/material/Button';
import { Agency } from '../redux/models'


let AgencyList = () => {

    const agencies = useAppSelector(state => state.agency.agencies)
    const agenciesStatus = useAppSelector(state => state.agency.status)
    const dispatch = useAppDispatch()

    const doSelectAgency = (agency: Agency | null) => {
        dispatch(selectAgency(agency))
    }

    const renderedAgencies = agencies.map(a => (
        <div className="agency-container" key={a.id}>
            <h3>{a.agency_name}</h3>
            <p className="agency-content">{a.agency_url.substring(0, 100)}</p>
            <Button variant="outlined" onClick={() => doSelectAgency(a)}>Routes</Button>
        </div>
    ))

    useEffect(() => {
        if (agenciesStatus === 'idle') {
            dispatch(fetchAgencies())
        }
    }, [agenciesStatus, dispatch])

    return (
        <React.Fragment>

            <div id="agency-list">
                {agenciesStatus === 'loading' ?
                    "loading..."
                    : agenciesStatus === 'succeeded' ?
                        renderedAgencies
                        : "error"
                }

            </div>
        </React.Fragment>
    );

}

export default AgencyList;