import React, { useState } from 'react';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Home from './routes/Home';
import Login from './routes/Login';
import Preferences from './routes/Preferences'
import useToken from './useToken'
import Logs from './routes/Logs'
import Account from './routes/Account'

function App() {
  const { token, setToken } = useToken();
  if (!token) {
    return <Login setToken={setToken} />
  }
  const logout = () => setToken(undefined)
  return (
    <div className="wrapper">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home logout={logout} />} />
          <Route path="/Logs" element={<Logs logout={logout} />} />
          <Route path="/Account" element={<Account logout={logout} />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
