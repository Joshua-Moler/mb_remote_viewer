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
        return (
            <div style={
                {
                    "visibility": this.props.visibility,
                    "zIndex": this.props.z,
                    "background": this.props.background


                }
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



