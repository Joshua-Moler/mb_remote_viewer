import '../style.css'
import Footer from '../components/Footer';
import CardHolder from '../components/CardHolder';
import { useEffect, useState } from 'react'
import BoardController from '../components/BoardController';
import PumpMonitor from '../components/PumpMonitor';
import serverParameters from '../data/serverParameters.json';
import useInterval from '../useInterval'
import logo from "../logo.svg"
import TurboPump from '../components/TurboPump';

const backendHost = serverParameters['Backend_Host']



function Control(props) {


    let state = {

        "v1": false,
        "v2": false,
        "v3": false,
        "v4": false,
        "v5": false,
        "v6": false,
        "v7": false,
        "v8": false,
        "v9": false,
        "v10": false,
        "v11": false,
        "v12": false,
        "v13": false,
        "v14": false,
        "v15": false,
        "v16": false,
        "v17": false,
        "v18": false,
        "v19": false,
        "v20": false,
        "v21": false,
        "v22": false,
        "v23": false,
        "v24": false,
        "PM1": false,
        "PM2": false

    }

    const [status, setStatus] = useState(state)
    const [userStatus, setUserStatus] = useState(state)
    const [isChanging, setIsChanging] = useState(false)
    const [waiting, setWaiting] = useState(true)
    const [pumpManagerOn, setPumpManagerOn] = useState("")
    const [opSuccess, setOpSuccess] = useState(true)

    const updateStatus = () => {


        fetch(`${backendHost}/status`, { method: 'GET', credentials: 'include' }).
            then(data => data.json()).
            then(json => {
                console.log("STATE RECIEVED: ", json)
                for (var key in status) {
                    if (json[key] === undefined) {
                        json[key] = status[key]
                    }
                }


                setStatus(

                    json

                )

                var isSameState = true

                for (let key in json) {
                    if (json[key] != userStatus[key]) {
                        isSameState = false
                    }
                }

                if (!isChanging || isSameState) {
                    setUserStatus(json)
                    setIsChanging(false)
                }
                setWaiting(false)
            })


    }

    const sendRequest = () => {
        setWaiting(true)
        fetch(`${backendHost}/setstate`, { method: 'POST', body: JSON.stringify(userStatus), credentials: 'include' }).
            then(data => data.json()).
            then(json => {

                if (json[0] == false) {
                    console.log('failed')
                    return
                }
                setOpSuccess(json[0])
                let newState = json[1]
                console.log(newState)
                for (var key in status) {
                    if (newState[key] === undefined) {
                        newState[key] = status[key]
                    }
                }


                setStatus(

                    newState

                )

                // var isSameState = true

                // for (let key in json) {
                //     if (json[key] != userStatus[key]) {
                //         isSameState = false
                //     }
                // }
                console.log(json)

                setUserStatus(newState)
                setIsChanging(false)

                setWaiting(false)
            })

    }

    const requestChange = () => {
        if (isChanging) {

            return (<div style={{ "color": "white", position: "absolute", "bottom": 0, right: "0%", background: "none", "height": "10%", "width": "100%", display: "flex", alignItems: "center" }}>
                <div style={{ userSelect: "none", background: "none", marginLeft: "25%", fontSize: "Large", borderColor: "white", borderTopStyle: "solid", borderLeftStyle: "solid", borderBottomStyle: "solid", borderRightStyle: 'solid', borderWidth: "1px", width: "60%", height: "50%", display: "flex", alignItems: "center", justifyContent: "center", textJustify: "center", zIndex: "20" }}
                    onClick={() => sendRequest()}
                >
                    Request Changes
                </div>
            </div>)
        }
        return ("")
    }

    useEffect(() => {
        props.setPage();
        setWaiting(true)
        updateStatus(true)



    }, [])

    useInterval(() => {
        updateStatus()

    }, 10000);

    const handleMapClick = (id) => {
        var isSameState = checkSameState(id)

        setUserStatus(prevState => ({ ...prevState, [id]: !prevState[id] }))
        setIsChanging(!isSameState)
    }

    const updating = () => {
        if (waiting) {
            return (<div style={{ position: "absolute", top: "0", left: "25vw", width: "75vw", height: "100vh", background: "rgb(0,0,0,0.5)", zIndex: "30", overflow: "hidden", color: "white", display: "flex", justifyContent: "center", alignItems: "center" }}>
                <img className='App-logo' src={logo}></img>
            </div>)
        }
        return ""
    }

    const checkSameState = (id) => {

        var isSameState = true
        for (let key in status) {
            if (status[key] != userStatus[key] && (id === undefined || key != id)) {
                isSameState = false
            }
        }

        if (status[id] === userStatus[id] && id !== undefined) {
            isSameState = false
        }

        return isSameState
    }

    const pumpMonitorManage = (id) => {
        setPumpManagerOn(id)
    }


    const pumpSetpointUpdateButton = (id, setPoint, input) => {

    }

    const pumpManager = (id) => {
        if (pumpManagerOn === '') return '';
        return (
            <div style={{ position: "absolute", top: "0", left: "25vw", width: "75vw", height: "100vh", overflow: "hidden", display: 'grid', placeItems: 'center' }}>
                <div style={{ position: 'relative', width: '50%', background: "rgba(255,255,255,0.1)", backdropFilter: "blur(10px)", zIndex: "31", borderColor: "white", borderStyle: "solid", borderWidth: "1px", color: "white", display: "flex" }} onClick={() => console.log('clicked')}>
                    <div style={{ width: "35%", display: "flex", alignItems: "center", flexDirection: 'column', pointerEvents: 'none', userSelect: 'none', flex: 1 }}>
                        <div style={{ marginTop: "15%", display: 'flex', justifyContent: 'center' }}>
                            <div style={{ fontSize: '36px', color: "white" }}> {id} </div>
                            <div style={{ marginLeft: "20px" }}>
                                <TurboPump status={status[id]} />
                            </div>
                        </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> State:  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> Rotor Speed:  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> Converter Temp:  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> Motor Temp:  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> Bearing Temp:  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%", marginBottom: "15%" }}> Setpoint:  </div>

                    </div>

                    <div style={{ width: "35%", display: "flex", alignItems: "center", flexDirection: 'column', userSelect: 'none', flex: 1 }}>
                        <div style={{ fontSize: '36px', color: "transparent", marginTop: "15%" }}> {id} </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> idle  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> 0 Hz  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> 25 C  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> 25 C  </div>
                        <div style={{ fontSize: '24px', color: "white", marginTop: "15%" }}> 25 C  </div>
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: "15%" }}>
                            <input type="text" style={{ fontSize: '24px', color: "white", marginTop: "15%", marginLeft: "10%", background: 'none', width: '25%', textAlign: 'center', placeholder: '1000' }} />
                            <div style={{ fontSize: '24px', color: "white", marginTop: "15%", marginLeft: "10px" }}> Hz  </div>
                        </div>
                    </div>




                </div>

                <div style={{ position: "absolute", top: "0", left: "0", width: "100%", height: "100%", background: "rgb(0,0,0,0.5)", zIndex: "30", overflow: "hidden" }} onClick={() => { pumpMonitorManage(""); console.log('also clicked') }} />
            </div>
        )
    }

    return (
        <div className="LogsScreen">

            {updating()}

            <div style={{ marginLeft: "25vw", top: "10vh", height: "100%", width: "75vw", display: "flex", justifyContent: "flex-end", alignItems: "flex-start", background: "none", overflow: "hidden" }}>
                <BoardController status={userStatus} handleClick={handleMapClick} />
                <div style={{ display: "flex", justifyContent: "flex-start", alignItems: "center", height: "100%", width: "300px", background: "none", flexDirection: "column", position: "relative" }}>
                    <PumpMonitor id="PM1" color={userStatus['PM1'] ? '#00bbff' : '#ff00aa'} status={userStatus["PM1"] ? "Running" : "Idle"} statorFrequency={0} handleClick={pumpMonitorManage} />
                    <PumpMonitor id="PM2" color={userStatus['PM2'] ? '#00bbff' : '#ff00aa'} status={userStatus["PM2"] ? "Running" : "Idle"} statorFrequency={0} handleClick={pumpMonitorManage} />
                    {requestChange()}
                </div>

            </div>

            {pumpManager(pumpManagerOn)}



        </div >
    );
}

export default Control;