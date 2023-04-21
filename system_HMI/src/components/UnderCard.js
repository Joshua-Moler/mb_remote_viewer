import React, { Component } from 'react';

export default class UnderCard extends Component {
    constructor(props) {
        super(props);
        this.state = { fade: false }
        this.displayText = this.props.text ? this.props.text : "Click Me"
        this.state = { count: 0 }

    }


    render() {
        const fade = this.state.fade
        const style = {
            "visibility": this.props.visibility,
            "zIndex": this.props.z,
            "background": this.props.background,
            "backdropFilter": "blur(20px)",
            "position": "absolute",
            "top": `${this.props.top}vh`,
            "height": `${this.props.height}vh`
        }
        if (1)
            style["transition"] = "top 0.5s"
        return (
            <div style={
                style
            }
                onClick={() => { this.props.onClick(this.props.text); }}


                className={`undercard`}>
                <div style={{ "marginLeft": "5%", "paddingTop": '0.5%', 'fontWeight': 'bold' }}>
                    {`${this.props.value} ${this.props.units}`}
                </div>
                <div style={{ "marginLeft": "5%", "fontSize": "x-small" }}>
                    {`${this.props.text}`}
                </div>
            </div>
        )
    }
}



