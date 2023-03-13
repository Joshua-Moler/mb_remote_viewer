import logo from '../logo.svg';
import { Link } from 'react-router-dom';
import '../App.css';
import '../style.css'
import Footer from '../components/Footer';
import CardHolder from '../components/CardHolder';

function Home(props) {



    return (
        <div className="App">
            <div className="App-header">
                {/* <img src={logo} className="App-logo" alt="logo" />
                <p>
                    Edit <code>src/App.js</code> and save to reload.
                </p>
                <a
                    className="App-link"
                    href="https://reactjs.org"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Learn React
                </a> */}
            </div>
            <CardHolder />
            <Footer logout={props.logout} active="Home" />
            {/* <div className='testing' /> */}

        </div >
    );
}

export default Home;
