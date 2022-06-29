import React from "react";
import { useAppSelector, useAppDispatch } from '../hooks'
import { showNavModal } from "../redux/features/nav";
import { logoutUser } from "../redux/features/auth";
import Button from '@mui/material/Button';



let Header = () => {

    const dispatch = useAppDispatch()
    const auth = useAppSelector(state => state.auth);

    const handleLoginClick = () => {
        dispatch(showNavModal())
    }
    const handleLogoutClick = () => {
        dispatch(logoutUser())
    }

    return (
        <React.Fragment>
            <div className="header">
                <div className="header-logo-container">
                    {"Logo"}
                </div>
                <div className="header-title-container">
                    {"Header"}
                </div>
                <div className="header-button-container">
                    {!auth.token
                        ? <Button variant="outlined" color="success" onClick={handleLoginClick}> Login</Button>
                        : <Button variant="outlined" color="success" onClick={handleLogoutClick}> Logout</Button>}
                </div>
            </div>
        </React.Fragment>
    );
}

export default Header;