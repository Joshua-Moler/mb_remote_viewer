import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Home from './routes/Home';
import Login from './routes/Login';
import Preferences from './routes/Preferences'
import usePermissions from './usePermissions'
import Logs from './routes/Logs'
import Control from './routes/Control'
import Footer from './components/Footer';
import { useLocation } from 'react-router-dom';
import CardHolder from './components/CHFUNC';


import { io } from "socket.io-client";

const socket = io('ws://localhost:8081', { path: '/socket.io/', transports: ['websocket', 'polling'] });



function App() {
  const { permissions, setPermissions } = usePermissions();
  const [activePage, setActivePage] = useState("Home");
  const [embedded, setEmbedded] = useState(false)

  const [sioConnected, setSioConnected] = useState(socket.connected)

  const [values, setValues] = useState({ "TEMPERATURES": {}, "PRESSURES": {}, "FLOWS": {}, "SETPOINT": {}, "STATUS": {}, "VALVES": {}, "PUMPS": {}, "TURBOS": {} })

  useEffect(() => {

    function onConnect() {
      setSioConnected(true);
    }

    function onDisconnect() {
      setSioConnected(false);
    }

    function onValues(newValues) {
      setValues(prevState => {
        for (let value in prevState) {
          if (newValues[value] === undefined) {
            newValues[value] = prevState[value]
          }
        }
        return newValues
      })
      //console.log(values)
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
  //   return <Login setPermissions={setPermissions} />
  // }
  //const logout = () => { setPermissions(false); fetch("http://localhost:8000/logout", { method: 'POST', credentials: 'include' }) }
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
          values={{ "TEMPERATURES": values["TEMPERATURES"], "PRESSURES": values["PRESSURES"], "FLOWS": values["FLOWS"], "STATUS": values["STATUS"], "SETPOINT": values["SETPOINT"] }} />
        <Footer logout={logout} active={activePage} embedded={embedded} />
      </BrowserRouter>
    </div>
  );
}

export default App;
