import '../style.css'
import Footer from '../components/Footer';
import CardHolder from '../components/CardHolder';


function Control(props) {



    return (
        <div className="LogsScreen">
            <CardHolder embedded={true} />
            <Footer logout={props.logout} active="Control" embedded={true} />
            {/* <div className='testing' /> */}

        </div >
    );
}

export default Control;