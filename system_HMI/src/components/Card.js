import React, { Component } from 'react';

export default class Card extends Component {
    constructor(props) {
        super(props);
        this.displayText = this.props.text ? this.props.text : ""
        this.state = { count: 0 }
    }

    render() {
        const fade = this.props.fade

        return (
            <div style={
                {
                    "marginTop": `${fade ? this.props.padding : 0}vh`,
                    "borderWidth": `${this.displayText ? 0.1 : 0}vh`,
                    "background": this.props.background,
                    "backdropFilter": "blur(20px)",
                    "zIndex": 35

                }

            }

                onClick={() => {
                    //this.setState({ fade: !fade });
                    this.props.onClick(this.props.id)
                }}

                className={`fade`}>
                <div style={{ "marginLeft": "10%", "fontWeight": "bold" }}>
                    {`${this.props.value} ${this.props.units ? this.props.units : ""}`}
                </div>
                <div style={{ "fontSize": "small", "marginLeft": "10%" }}>
                    {`${this.props.text}`}
                </div>
            </div >
        )
    }
}