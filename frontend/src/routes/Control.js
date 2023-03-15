import '../style.css'
import Footer from '../components/Footer';
import CardHolder from '../components/CardHolder';
import { useEffect } from 'react'
import BoardController from '../components/BoardController';


function Control(props) {

    useEffect(() => { props.setPage() })

    return (
        <div className="LogsScreen" >
            <div style={{ marginLeft: "25vw", top: "10vh", height: "100%", width: "70vw", display: "flex", justifyContent: "center", alignItems: "center" }}>
                <BoardController />
            </div>

        </div >
    );
}

export default Control;