import logo from '../test.png';
import '../style.css'
import Footer from '../components/Footer';
import React, { useState } from 'react';
import Plot from '../components/Plot';


function Logs(props) {



    return (
        <div className="LogsScreen">
            <div style={{
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "flexDirection": "column"
            }}>
                <div style={{
                    "height": "5vh",
                }}>
                </div>

                <div style={{
                    "width": "100vw",
                    "height": "50vh",
                    "background": "none",





                }}>

                    <Plot />

                </div>
            </div>
            <Footer logout={props.logout} active="Logs" />
            {/* <div className='testing' /> */}

        </div >
    );
}

export default Logs;