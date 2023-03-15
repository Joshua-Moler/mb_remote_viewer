import ValveButton from "./ValveButton";
import ValveBoard from '../components/ValveBoard';


function BoardController(props) {

    const positions = {
        "v1": { left: "30%", top: "10%", horizontal: false },
    }

    const ValveButtons = Object.keys(positions).map(ii =>
        <ValveButton left={positions[ii].left} top={positions[ii].top} horizontal={positions[ii].horizontal} id={ii} key={ii} />
    )
    let _1vh = Math.round(window.innerHeight)
    return (
        <div style={{ "width": "95%", "paddingTop": "0%", maxWidth: `${_1vh}px` }}>
            {ValveButtons}
            <ValveBoard />

        </div>
    );
}

export default BoardController;