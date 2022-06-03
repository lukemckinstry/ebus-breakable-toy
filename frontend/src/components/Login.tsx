import React, { useState, useRef, useEffect } from "react";
import { useAppSelector, useAppDispatch } from '../hooks'
import { hideNavModal } from "../redux/features/nav";
import { registerUser, loginUser } from "../redux/features/auth";
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';

interface LoginForm {
  email: string,
  username: string,
  password: string,
}

const defaultInputs: LoginForm = {
  email: "",
  username: "",
  password: "",
}


let Login = (props: any) => {
  const dispatch = useAppDispatch()
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [selectedBtn, setSelectedBtn] = useState(1);
  const [inputs, setInputs] = useState<LoginForm>(defaultInputs);
  const status = useAppSelector(state => state.auth.status)


  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside, false);
    return () => {
      document.removeEventListener("mounsedown", handleClickOutside, false);
    };
  }, []);

  const handleClickOutside = (event: any) => {
    if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
      dispatch(hideNavModal())
    }
  };

  const handleClose = () => {
    dispatch(hideNavModal())
  }

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = event.target.value;
    setInputs(values => ({ ...values, [name]: value }))
  }

  const handleLoginSubmit = (event: any) => {
    event.preventDefault();
    dispatch(loginUser(inputs))
    setInputs(defaultInputs)
  }

  const renderLoginForm = () => {
    return (
      <form onSubmit={handleLoginSubmit}>
        <label>Email:
          <input
            type="text"
            name="email"
            value={inputs.email}
            onChange={handleChange}
          />
        </label>
        <label>Password:
          <input
            type="text"
            name="password"
            value={inputs.password}
            onChange={handleChange}
          />
        </label>
        <input type="submit" value="Login" />
      </form>
    )
  }

  const handleRegisterSubmit = (event: any) => {
    event.preventDefault();
    dispatch(registerUser(inputs))
  }

  const renderRegistrationForm = () => {
    return (
      <form onSubmit={handleRegisterSubmit}>
        <label>Email:
          <input
            type="text"
            name="email"
            value={inputs.email}
            onChange={handleChange}
          />
        </label>
        <label>Username:
          <input
            type="text"
            name="username"
            value={inputs.username}
            onChange={handleChange}
          />
        </label>
        <label>Password:
          <input
            type="text"
            name="password"
            value={inputs.password}
            onChange={handleChange}
          />
        </label>
        <input type="submit" value="Register" />
      </form>
    )
  }

  const render = () => {
    return (
      <div className="modal" >
        <div className="modal-content" ref={wrapperRef}>
          <div className="modal-content-header">
            <span className="close" onClick={handleClose}>&times;</span>
            <p>Some text in the Modal.</p>
          </div>
          <div className="modal-content-selector">
            <ButtonGroup disableElevation variant="contained" color="primary">
              <Button variant={selectedBtn === 1 ? "contained" : "outlined"} onClick={() => setSelectedBtn(1)}>Login</Button>
              <Button variant={selectedBtn === 2 ? "contained" : "outlined"} onClick={() => setSelectedBtn(2)}>Register</Button>
            </ButtonGroup>

          </div>
          <div className="modal-content-form">
            {selectedBtn === 1
              ? renderLoginForm()
              : renderRegistrationForm()}
          </div>
          <div className="modal-content-status">

            {status && (<p>{status}</p>)}
          </div>
        </div>
      </div>
    )
  }

  return (
    render()

  );
}

export default Login;
