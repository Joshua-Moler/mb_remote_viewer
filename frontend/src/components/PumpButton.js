function PumpButton(props) {


    return (
        <div style={{
            "width": '5%', "height": '5%', "background": "none", "left": `${props.left}`, "top": `${props.top}`, "position": "absolute", "borderRadius": "50%", "zIndex": "10"
        }} onClick={props.onClick}>
        </div>
    );
}

export default PumpButton;