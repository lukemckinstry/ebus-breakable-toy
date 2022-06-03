import React, { useEffect, useRef, useState, Dispatch } from "react";
import { useAppSelector, useAppDispatch } from '../hooks'
import { selectAgency } from "../redux/features/agency";
import { fetchRoutes, updateRoute } from "../redux/features/route";
import { loginUser } from "../redux/features/auth";
import { showNavModal } from "../redux/features/nav";
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Switch from '@mui/material/Switch';


let RouteDetail = () => {

    const routes = useAppSelector(state => state.route.routes)
    const routesStatus = useAppSelector(state => state.route.status)
    const selectedRoute = useAppSelector(state => state.route.selectedRoute)
    const selectedAgency = useAppSelector(state => state.agency.selectedAgency)
    const auth = useAppSelector(state => state.auth);
    const dispatch = useAppDispatch()
    const [edit, setEdit] = useState(false)
    const [zevChargingInfrastrucutre, setZevChargingInfrastrucutre] = useState<boolean | undefined>(selectedRoute?.zev_charging_infrastructure || false)
    const [zevNotes, setZevNotes] = useState<string | undefined>(selectedRoute?.zev_notes || "")
    const [pctZevService, setPctZevService] = useState<number | undefined>(selectedRoute?.pct_zev_service || 0)
    const [numZev, setNumZev] = useState<number | undefined>(selectedRoute?.num_zev || 0)

    const toggleEdit = () => {
        setEdit(!edit)
    }

    const clickLogin = () => {
        dispatch(showNavModal())
    }

    const handleSave = () => {
        if (!selectedRoute) { return }
        const changes = {
            zev_charging_infrastructure: zevChargingInfrastrucutre,
            zev_notes: zevNotes,
            pct_zev_service: pctZevService,
            num_zev: numZev
        }
        const args = {
            route: selectedRoute,
            changes: changes,
            updatedAt: new Date().toISOString()
        }
        dispatch(updateRoute(args))
        toggleEdit()
    }

    const handleZevNotesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setZevNotes(e.currentTarget.value)
    }

    const handlePctZevServiceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseInt(e.currentTarget.value) || 0
        setPctZevService(val)
    }

    const handleNumZevChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseInt(e.currentTarget.value) || 0
        setNumZev(val)
    }

    const handleInfrastructureChange = () => {
        setZevChargingInfrastrucutre(!zevChargingInfrastrucutre)
    }

    const bottomForm = () => (
        <div className="route-detail-bottom">
            <div className="form-top-row">
                <div className="form-top-row-section">
                    <div className="form-switch-container">
                        <div className="form-top-row-section-label">ZEV Infrastructure Installed</div>
                        <Switch
                            checked={zevChargingInfrastrucutre}
                            onChange={handleInfrastructureChange}
                            inputProps={{ 'aria-label': 'controlled' }}
                        />
                    </div>
                </div>
                <div className="form-top-row-section">
                    <div className="form-top-row-section-label">Pct ZEV Service</div>
                    <TextField
                        inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                        value={pctZevService}
                        onChange={handlePctZevServiceChange}
                        size="small"
                    />
                </div>
                <div className="form-top-row-section">
                    <div className="form-top-row-section-label">Num ZEV Vehciles</div>
                    <TextField
                        inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                        value={numZev}
                        onChange={handleNumZevChange}
                        size="small"
                    />
                </div>
            </div>
            <div className="form-bottom-row">
                <div className="form-bottom-row-label">ZEV Notes</div>
                <div className="form-bottom-row-content">
                    <TextField
                        id="outlined-multiline-flexible"
                        multiline
                        maxRows={4}
                        value={zevNotes}
                        onChange={handleZevNotesChange}
                        fullWidth
                        size="small"
                    />
                </div>
            </div>

        </div>
    )

    const bottomDisplay = () => (
        <div className="route-detail-bottom">
            <div className="route-detail-bottom-field">
                Has ZEV charging Infrastructure: {zevChargingInfrastrucutre ? "True" : "False"}
            </div>
            <div className="route-detail-bottom-field">
                Pct ZEV Service: {pctZevService}
            </div>
            <div className="route-detail-bottom-field">
                Num ZEV Vehicles: {numZev}
            </div>
            <div className="route-detail-bottom-field">
                ZEV Notes: {zevNotes}
            </div>
        </div>
    )


    const scheduleTable = () => {
        const s = selectedRoute
        return (
            <table className="route-schedule-table">
                <thead>
                    <tr>
                        <th>Mon</th>
                        <th>Tue</th>
                        <th>Wed</th>
                        <th>Thu</th>
                        <th>Fri</th>
                        <th>Sat</th>
                        <th>Sun</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{s?.trips_monday}</td>
                        <td>{s?.trips_tuesday}</td>
                        <td>{s?.trips_wednesday}</td>
                        <td>{s?.trips_thursday}</td>
                        <td>{s?.trips_friday}</td>
                        <td>{s?.trips_saturday}</td>
                        <td>{s?.trips_sunday}</td>
                    </tr>
                </tbody>
            </table>

        )
    }

    useEffect(() => {
        if (routesStatus === 'idle' && selectedAgency) {
            dispatch(fetchRoutes(selectedAgency.id))
        }
    }, [routesStatus, dispatch])

    return (
        <div className="route-selected-container" key={selectedRoute?.id}>
            <div className="route-selected-container-top-section">
                <h3>{selectedRoute?.route_long_name}</h3>
                <h3>{selectedRoute?.route_id}</h3>
            </div>

            {scheduleTable()}
            <p className="route-selected-content">{selectedRoute?.route_url.substring(0, 100)}</p>
            <div className="route-selected-bottom-container">
                {edit
                    ? bottomForm()
                    : bottomDisplay()}
            </div>

            <div className="route-selected-button-container">
                {edit
                    ? <React.Fragment>
                        <div className="route-selected-button-section">
                            <Button variant="outlined" color="success" onClick={handleSave} fullWidth>Save</Button>
                        </div>
                        <div className="route-selected-button-section">
                            <Button variant="outlined" color="error" onClick={toggleEdit} fullWidth>Cancel</Button>
                        </div>
                    </React.Fragment>

                    :
                    auth.token
                        ? <div className="route-selected-button-section">
                            <Button variant="outlined" color="error" onClick={toggleEdit} fullWidth>Edit</Button>
                        </div>
                        : <div className="route-selected-button-section">
                            <Button variant="outlined" onClick={clickLogin} fullWidth>Login to Edit</Button>
                        </div>
                }
            </div>
        </div>
    );

}

export default RouteDetail;