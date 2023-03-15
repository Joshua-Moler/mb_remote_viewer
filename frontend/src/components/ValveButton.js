function ValveButton(props) {


    return (
        <div style={{
            "width": `${props.horizontal ? "100vw" : "10%"}`, "height": `${props.horizontal ? "100vw" : "10%"}`, "background": "white", "left": `${props.left}`, "top": `${props.top}`, "position": "absolute"
        }}>
        </div>
    );
}

export default ValveButton;