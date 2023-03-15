import '../style.css'
import Footer from '../components/Footer';
import CardHolder from '../components/CardHolder';
import { useEffect } from 'react'


function Control(props) {

    useEffect(() => { props.setPage() })

    return (
        <div className="LogsScreen">
            {/* <div className='testing' /> */}

        </div >
    );
}

export default Control;