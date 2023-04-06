import React, { useState } from 'react';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Home from './routes/Home';
import Login from './routes/Login';
import Preferences from './routes/Preferences'
import useToken from './useToken'
import Logs from './routes/Logs'
import Control from './routes/Control'
import Footer from './components/Footer';
import { useLocation } from 'react-router-dom';
import CardHolder from './components/CardHolder';

function App() {
  const { token, setToken } = useToken();
  const [activePage, setActivePage] = useState("Home");
  const [embedded, setEmbedded] = useState(false)
  if (!token) {
    return <Login setToken={setToken} />
  }
  const logout = () => { setToken(false); fetch("http://localhost:8000/logout", { method: 'POST', credentials: 'include' }) }
  return (
    <div className="wrapper">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home setPage={() => { setActivePage("Home"); setEmbedded(false) }} />} />
          <Route path="/Logs" element={<Logs setPage={() => { setActivePage("Logs"); setEmbedded(true) }} />} />
          <Route path="/Control" element={<Control setPage={() => { setActivePage("Control"); setEmbedded(true) }} />} />
        </Routes>
        <CardHolder embedded={embedded} />
        <Footer logout={logout} active={activePage} embedded={embedded} />
      </BrowserRouter>
    </div>
  );
}

export default App;
