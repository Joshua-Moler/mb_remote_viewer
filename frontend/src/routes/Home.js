import logo from '../logo.svg';
import { Link } from 'react-router-dom';
import '../App.css';
import '../style.css'
import Footer from '../components/Footer';
import CardHolder from '../components/CardHolder';
import { useEffect } from 'react'

function Home(props) {

    useEffect(() => { props.setPage() })

    return (
        <div className="LogsScreen">
            {/* <div className='testing' /> */}

        </div >
    );
}

export default Home;
