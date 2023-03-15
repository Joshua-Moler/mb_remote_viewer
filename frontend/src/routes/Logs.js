import logo from '../test.png';
import '../style.css'
import Footer from '../components/Footer';
import React, { useState } from 'react';
import Plot from '../components/Plot';
import CardHolder from '../components/CardHolder';
import { useEffect } from 'react'


function Logs(props) {

    useEffect(() => { props.setPage() })

    return (
        <div className="LogsScreen">
            <div style={{
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "flexDirection": "column",
                "width": "100%",
            }}>


                <div style={{
                    "width": "100%",
                    "height": "50vh",
                    "background": "none",

                }}>
                    <Plot />

                </div>
            </div>

        </div >
    );
}

export default Logs;