import React, { useState, useEffect } from 'react';
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
import CardHolder from './components/CHFUNC';

import { io } from "socket.io-client";

const socket = io('ws://localhost:8080', { path: '/socket.io/', transports: ['websocket', 'polling'] });



function App() {
  const { token, setToken } = useToken();
  const [activePage, setActivePage] = useState("Home");
  const [embedded, setEmbedded] = useState(false)

  const [sioConnected, setSioConnected] = useState(socket.connected)

  const [values, setValues] = useState({ "TEMPERATURES": {}, "PRESSURES": {}, "FLOWS": {}, "STATUS": {}, "VALVES": {}, "PUMPS": {}, "TURBOS": {} })

  useEffect(() => {

    function onConnect() {
      setSioConnected(true);
    }

    function onDisconnect() {
      setSioConnected(false);
    }

    function onValues(newValues) {
      console.log(newValues)
      setValues(prevState => {
        for (let value in prevState) {
          if (newValues[value] === undefined) {
            newValues[value] = prevState[value]
          }
        }
        return newValues
      })
    }

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('values', onValues);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('values', onValues)
    }


  }, [])



  // if (!token) {
  //   return <Login setToken={setToken} />
  // }
  const logout = () => { setToken(false); fetch("http://localhost:8000/logout", { method: 'POST', credentials: 'include' }) }
  return (
    <div className="wrapper">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home setPage={() => { setActivePage("Home"); setEmbedded(false) }} />} />
          <Route path="/Logs" element={<Logs setPage={() => { setActivePage("Logs"); setEmbedded(true) }} />} />
          <Route path="/Control" element={<Control setPage={() => { setActivePage("Control"); setEmbedded(true) }}
            values={{ "VALVES": values["VALVES"], "PUMPS": values["PUMPS"], "TURBOS": values["TURBOS"] }} />} />
        </Routes>
        <CardHolder embedded={embedded}
          values={{ "TEMPERATURES": values["TEMPERATURES"], "PRESSURES": values["PRESSURES"], "FLOWS": values["FLOWS"], "STATUS": values["STATUS"] }} />
        <Footer logout={logout} active={activePage} embedded={embedded} />
      </BrowserRouter>
      {String(values["TEMPERATURES"]['t1'])}
    </div>
  );
}

export default App;
