import React, { useState } from 'react';
import PropTypes from 'prop-types';

import './Login.css';
import serverParameters from '../data/serverParameters.json';

const backendHost = serverParameters['Backend_Host']

async function loginUser(credentials) {
    return fetch(`${backendHost}/login`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': "http://localhost:3000"
        },
        body: JSON.stringify(credentials)
    })
        .then(data => data.json())
}

export default function Login({ setToken }) {
    const [username, setUserName] = useState('');
    const [password, setPassword] = useState('');
    const [invalidCredentials, setInvalidCredentials] = useState("none");

    const handleSubmit = async e => {
        document.getElementById("Login-Form").reset()
        e.preventDefault();
        if (username === '' || password === '') {
            setInvalidCredentials("empty")
            return
        }
        const logInJson = await loginUser({
            username, password
        });
        let token = ''
        if (logInJson["authenticated"] === true && logInJson['token']) {
            token = logInJson['token']
        }
        else if (logInJson['authenticated'] === false) {
            setInvalidCredentials("invalid")
        }

        setToken({ 'token': true })
    }

    const displayInvalid = () => {
        if (invalidCredentials === "invalid") {
            return (
                <div style={{ color: "red" }}>
                    Invalid Credentials
                </div>
            )
        }
        else if (invalidCredentials === 'empty') {
            return (
                <div style={{ color: "blue" }}>
                    Please Provide Login Information
                </div>)
        }
        else {
            return ("")
        }
    }

    return (
        <div className="login-wrapper">
            <h1>Please Log In</h1>
            <form onSubmit={handleSubmit} id="Login-Form">
                <label>
                    <p>Username</p>
                    <input type="text" onChange={e => setUserName(e.target.value)} />
                </label>
                <label>
                    <p>Password</p>
                    <input type="password" onChange={e => setPassword(e.target.value)} />
                </label>
                <div>
                    <button type="submit">Submit</button>
                </div>
            </form>
            {displayInvalid()}
        </div>
    )
}

Login.propTypes = {
    setToken: PropTypes.func.isRequired
}

