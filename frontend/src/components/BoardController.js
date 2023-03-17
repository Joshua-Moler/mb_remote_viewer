import ValveButton from "./ValveButton";
import ValveBoard from '../components/ValveBoard';
import PumpButton from "./PumpButton";


function BoardController(props) {

    const positions = {
        "v1": { left: "65.75%", top: "7.5%", horizontal: false },
        "v2": { left: "74.25%", top: "7.5%", horizontal: false },
        "v3": { left: "65.75%", top: "26%", horizontal: false },
        "v4": { left: "74.25%", top: "26%", horizontal: false },
        "v5": { left: "60.75%", top: "22.25%", horizontal: true },
        "v6": { left: "60.75%", top: "17.75%", horizontal: true },
        "v7": { left: "73.25%", top: "82%", horizontal: true },
        "v9": { left: "56.5%", top: "82%", horizontal: true },
        "v10": { left: "69.75%", top: "76%", horizontal: false },
        "v11": { left: "26.7%", top: "77.25%", horizontal: true },
        "v12": { left: "23.2%", top: "62.5%", horizontal: false },
        // "v14": { left: "18.25%", top: "82%", horizontal: true },
        "v15": { left: "14.75%", top: "71.75%", horizontal: false },
        "v16": { left: "18.25%", top: "68.25%", horizontal: true },
        "v17": { left: "14.75%", top: "62.5%", horizontal: false },
        "v18": { left: "73.25%", top: "91.25%", horizontal: true },
        "v19": { left: "18.25%", top: "77.25%", horizontal: true },
        "v22": { left: "73.25%", top: "49.75%", horizontal: true },
        "v23": { left: "73.25%", top: "59%", horizontal: true },
        "v24": { left: "69.75%", top: "53.5%", horizontal: false },
    }

    const pumpPositions = {
        "PM1": { left: "31%", top: "67%", horizontal: false },
        "PM2": { left: "31%", top: "58%", horizontal: false },
        // "PM3": { left: "52%", top: "67%", horizontal: false },
        // "PM4": { left: "52%", top: "76%", horizontal: false },
        // "PM5": { left: "77.7%", top: "53.5%", horizontal: false },
    }

    const ValveButtons = Object.keys(positions).map(ii =>
        <ValveButton left={positions[ii].left} top={positions[ii].top} horizontal={positions[ii].horizontal} id={ii} key={ii} onClick={() => props.handleClick(ii)} />
    )

    const PumpButtons = Object.keys(pumpPositions).map(ii =>
        <PumpButton left={pumpPositions[ii].left} top={pumpPositions[ii].top} horizontal={pumpPositions[ii].horizontal} id={ii} key={ii} onClick={() => props.handleClick(ii)} />
    )

    let _1vh = Math.round(window.innerHeight)
    return (
        <div style={{ "width": "95%", "paddingTop": "0%", maxWidth: `${_1vh}px`, position: "relative", background: "none", marginLeft: "5%", marginRight: "2.5%", marginTop: "2.5%" }}>
            {ValveButtons}
            {PumpButtons}
            <div style={{ "width": "100%", "height": "100%", background: "none", position: "absolute" }} />
            <ValveBoard status={props.status} />

        </div>
    );
}

export default BoardController;