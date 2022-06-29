import React, { } from "react";
import { useAppSelector } from '../hooks'
import AgencyList from "./AgencyList";
import RouteList from "./RouteList";

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