
import React, { Component } from 'react';
import UnderCard from './UnderCard.js'

export default class CardHolder extends Component {
    constructor(props) {
        super(props);


    }



    render() {
        let doesDraw = [...Array(this.props.cardNum).keys()]
        for (var ii in this.props.labels) {
            if (this.props.labels[ii] === this.props.omit) {
                doesDraw.splice(ii, 1)
            }
        }
        let position = {}
        for (const key in doesDraw) {
            position[doesDraw[key]] = key
        }
        return (
            <div className={`undermain${this.props.embedded ? " embedded" : ""}`} style={{
                "top": `${this.props.active ? this.props.top : this.props.oldTop}vh`,
                "height": `${this.props.height > 0 ? this.props.height : 0}vh`,
                maxHeight: `${this.props.active ? this.props.height : 0}vh`,
                "overflow": "hidden",
                "position": "absolute",
                "zIndex": 1000
            }}>
                {doesDraw.map(ii =>
                    <UnderCard
                        background={this.props.background[0][ii]}
                        text={this.props.labels[ii]}
                        key={position[ii]}
                        onClick={(e) => this.props.onClick(e, this.props.id)}
                        visibility={this.props.visibility}
                        z={this.props.active ? '34' : '33'}
                        value={this.props.values[this.props.labels[ii]]}
                        units={this.props.units}
                        top={position[ii] * this.props.height / doesDraw.length + (this.props.active ? 0 : this.props.top - this.props.oldTop)}
                        height={this.props.height / doesDraw.length}
                    />)}
            </div>
        )
    }
}