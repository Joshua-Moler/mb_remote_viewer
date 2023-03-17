import logo from '../test.png';
import '../style.css'
import Footer from '../components/Footer';
import React, { useState } from 'react';
import CardHolder from '../components/CardHolder';
import { useEffect } from 'react'
import serverParameters from '../data/serverParameters.json';
import useInterval from '../useInterval'


const backendHost = serverParameters['Backend_Host']

function Logs(props) {
    let _1vh = Math.round(window.innerHeight)

    const [imageUpdater, setImageUpdater] = useState(false)

    useEffect(() => { props.setPage() }, [])

    useInterval(() => {
        setImageUpdater(prevState => !prevState)

    }, 30000);

    return (
        // <div className="LogsScreen">
        //     <div style={{
        //         "display": "flex",
        //         "justifyContent": "center",
        //         "alignItems": "center",
        //         "flexDirection": "column",
        //         "width": "100%",
        //     }}>


        //         <div style={{
        //             "width": "100%",
        //             "height": "50vh",
        //             "background": "none",

        //         }}>
        //             <Plot />

        //         </div>
        //     </div>
        <div className='LogsScreen'>

            <div style={{ marginLeft: "25vw", top: "10vh", height: "100%", width: "75vw", display: "flex", justifyContent: "flex-end", alignItems: "flex-start", background: "none", overflow: "hidden" }}>
                <div style={{ "width": "95%", "height": "80%", position: "relative", backgroundImage: `url(${backendHost}/Plot/${imageUpdater})`, marginLeft: "2.5%", marginRight: "2.5%", marginTop: "2.5%", backgroundSize: "contain", backgroundRepeat: "no-repeat" }}>


                </div>

            </div>

        </div >
    );
}

export default Logs;