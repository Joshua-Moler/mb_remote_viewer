function PumpMonitor(props) {


    return (
        <div style={{ width: "100%", height: "100px", minHeight: "70px", background: "none", borderColor: "white", borderLeftStyle: "solid", borderBottomStyle: "solid", borderWidth: "1px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignitems: "center", background: "none" }}>
                <div style={{ fontWeight: "bold", fontSize: "20px", color: "white", marginLeft: "5%" }}>
                    {props.id}
                </div>
                <div style={{ color: props.color, flex: 1, background: "none", paddingTop: "1%", paddingLeft: "5%" }}>
                    {props.status}
                </div>
            </div>
            <div style={{ color: "white", marginLeft: "10%" }}>
                Stator Frequency: {props.statorFrequency}
            </div>
            <button style={{ background: "none", color: "white", width: "50%", borderColor: "white", borderTopStyle: "solid", borderLeftStyle: "solid", borderBottomStyle: "none", borderRightStyle: 'none', borderWidth: "1px", marginLeft: "10%", display: "flex", justifyContent: "center", marginBottom: "2%" }}
                onClick={() => props.handleClick(props.id)}>
                <div style={{ color: "white" }}>
                    Manage
                </div>
            </button>
        </div>
    );
}

export default PumpMonitor;