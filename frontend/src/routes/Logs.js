import logo from '../test.png';
import '../style.css'
import Footer from '../components/Footer';
import React, { useState } from 'react';
import Plot from '../components/Plot';
import CardHolder from '../components/CardHolder';


function Logs(props) {



    return (
        <div className="LogsScreen">
            <div style={{
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "flexDirection": "column",
                "width": "100%",
            }}>

                {/* <CardHolder embedded={true} /> */}

                <div style={{
                    "width": "100%",
                    "height": "50vh",
                    "background": "none",

                }}>
                    <Plot />

                </div>
            </div>
            <Footer logout={props.logout} active="Logs" embedded={true} />
            {/* <div className='testing' /> */}

        </div >
    );
}

export default Logs;