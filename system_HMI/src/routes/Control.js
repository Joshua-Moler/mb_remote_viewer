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


function getState(newValues) {
    let newState = {}

    for (let valve in newValues['VALVES']) {
        newState[valve] = newValues['VALVES'][valve]["STATE"] != undefined ? newValues['VALVES'][valve]["STATE"] : newValues['VALVES'][valve]
    }
    for (let pump in newValues['PUMPS']) {
        newState[pump] = newValues['PUMPS'][pump]["STATE"] != undefined ? newValues['PUMPS'][pump]["STATE"] : newValues['PUMPS'][pump]
    }
    for (let turbo in newValues['TURBOS']) {
        newState[turbo] = newValues['TURBOS'][turbo]["STATE"] != undefined ? newValues['TURBOS'][turbo]["STATE"] : newValues['TURBOS'][turbo]
    }
    return newState
}

function Control(props) {

    const status = getState(props.values)
    const [valves, setValves] = useState(props.values['VALVES'])
    const [pumps, setPumps] = useState(props.values['PUMPS'])
    const [turbos, setTurbos] = useState(props.values['TURBOS'])
    //console.log(props.values['VALVES'])
    const [userStatus, setUserStatus] = useState(status)
    const [isChanging, setIsChanging] = useState(false)
    const [waiting, setWaiting] = useState(false)
    const [pumpManagerOn, setPumpManagerOn] = useState("")


    let isSameState = true
    for (let device in status) {
        if (status[device] != userStatus[device]) {
            isSameState = false
            break;
        }
    }
    if (isSameState && isChanging) {
        setIsChanging(false)
    }
    else if (!isSameState && !isChanging) {
        setUserStatus(status)
    }



    // const updateStatus = () => {


    //     fetch(`${backendHost}/status`, { method: 'GET', credentials: 'include' }).
    //         then(data => data.json()).
    //         then(json => {
    //             console.log("STATE RECIEVED: ", json)
    //             for (var key in status) {
    //                 if (json[key] === undefined) {
    //                     json[key] = status[key]
    //                 }
    //             }


    //             setStatus(

    //                 json

    //             )

    //             var isSameState = true

    //             for (let key in json) {
    //                 if (json[key] != userStatus[key]) {
    //                     isSameState = false
    //                 }
    //             }

    //             if (!isChanging || isSameState) {
    //                 setUserStatus(json)
    //                 setIsChanging(false)
    //             }
    //             setWaiting(false)
    //         })


    // }

    const sendRequest = () => {
        setWaiting(true)
        fetch(`${backendHost}/system/set/all`, {
            method: 'POST', body: JSON.stringify(userStatus), credentials: 'include', headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': "http://localhost:3000"
            },
        }).
            then(data => data.json()).
            then(json => {
                console.log(json)

                if (json[0] == false) {
                    console.log('failed')
                }
                let newValues = json[1]

                setValves(newValues['VALVES'])
                setPumps(newValues['PUMPS'])
                setTurbos(newValues['TURBOS'])
                // console.log(newState)
                // for (var key in status) {
                //     if (newState[key] === undefined) {
                //         newState[key] = status[key]
                //     }
                // }


                // setStatus(

                //     newState

                // )

                // var isSameState = true

                // for (let key in json) {
                //     if (json[key] != userStatus[key]) {
                //         isSameState = false
                //     }
                // }
                //console.log(json)

                let newState = {}

                for (let valve in newValues['VALVES']) {
                    newState[valve] = newValues['VALVES'][valve]["STATE"] != undefined ? newValues['VALVES'][valve]["STATE"] : newValues['VALVES'][valve]
                }
                for (let pump in newValues['PUMPS']) {
                    newState[pump] = newValues['PUMPS'][pump]["STATE"] != undefined ? newValues['PUMPS'][pump]["STATE"] : newValues['PUMPS'][pump]
                }
                for (let turbo in newValues['TURBOS']) {
                    newState[turbo] = newValues['TURBOS'][turbo]["STATE"] != undefined ? newValues['TURBOS'][turbo]["STATE"] : newValues['TURBOS'][turbo]
                }
                console.log(newState)

                //setStatus(newState)
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




    }, [])


    const handleMapClick = (id) => {
        if (status[id] === undefined) {
            return
        }
        var newUserState = JSON.parse(JSON.stringify(userStatus))

        for (let device in status) {
            if (newUserState[device] === undefined) {
                newUserState[device] = status[device]
            }
        }

        newUserState[id] = !newUserState[id]
        let isSameState = true
        for (let device in status) {
            if (status[device] != newUserState[device]) {
                isSameState = false
                break;
            }
        }

        setUserStatus(newUserState)
        setIsChanging(!isSameState)
    }

    const updating = () => {
        if (waiting) {
            return (<div style={{ position: "absolute", top: "0", left: "24vw", width: "76vw", height: "100vh", background: "rgb(0,0,0,0.5)", zIndex: "30", overflow: "hidden", color: "white", display: "flex", justifyContent: "center", alignItems: "center" }}>
                <img className='App-logo' src={logo}></img>
            </div>)
        }
        return ""
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