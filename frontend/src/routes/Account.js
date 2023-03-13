import '../style.css'
import Footer from '../components/Footer';


function Logs(props) {



    return (
        <div className="LogsScreen">
            <div style={{
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "flexDirection": "column"
            }}>

            </div>
            <Footer logout={props.logout} active="Account" />
            {/* <div className='testing' /> */}

        </div >
    );
}

export default Logs;