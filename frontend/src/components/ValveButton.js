function ValveButton(props) {


    return (
        <div style={{
            "width": `${props.horizontal ? "5%" : "3%"}`, "height": `${props.horizontal ? "3%" : "5%"}`, "background": "none", "left": `${props.left}`, "top": `${props.top}`, "position": "absolute", "zIndex": "10"
        }} onClick={props.onClick}>
        </div>
    );
}

export default ValveButton;