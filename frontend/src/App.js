import React, { useState } from 'react';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Home from './routes/Home';
import Login from './routes/Login';
import Preferences from './routes/Preferences'
import useToken from './useToken'
import Logs from './routes/Logs'
import Control from './routes/Control'

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
          <Route path="/Control" element={<Control logout={logout} />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
