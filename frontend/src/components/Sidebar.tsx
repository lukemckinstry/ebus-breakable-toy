import React, { useEffect, useRef, useState, Dispatch } from "react";
import { useAppSelector, useAppDispatch } from '../hooks'
import { fetchAgencies } from "../redux/features/agency";
import AgencyList from "./AgencyList";
import styled from 'styled-components'
import RouteList from "./RouteList";


interface RouteProps {
    agency_id: string
}



let Sidebar = () => {

    // The `state` arg is correctly typed as `RootState` already
    const selectedAgency = useAppSelector(state => state.agency.selectedAgency)

    return (
        <React.Fragment>
            <div id="sidebar">
                {"Sidebar"}

                {selectedAgency ? <RouteList /> : <AgencyList />}

            </div>
        </React.Fragment>
    );
}

export default Sidebar;