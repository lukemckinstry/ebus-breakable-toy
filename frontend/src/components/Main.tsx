import React, { useState } from 'react';
import { useAppSelector, useAppDispatch } from '../hooks'

import Map from "./Map";
import Sidebar from './Sidebar';
import Header from './Header';
import Login from './Login';

let Main = () => {

  const login = useAppSelector(state => state.nav.showLoginModal);


  return (
    <React.Fragment>
      {login && <Login />}
      <Header />
      <Sidebar />
      <Map />

    </React.Fragment>
  );
}

export default Main;
