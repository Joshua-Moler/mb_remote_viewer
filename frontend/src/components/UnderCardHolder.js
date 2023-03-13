
import React, { Component } from 'react';
import UnderCard from './UnderCard.js'

export default class CardHolder extends Component {
    constructor(props) {
        super(props);


    }



    render() {

        return (
            <div className='undermain' style={{
                "top": `${this.props.top}vh`,
                "height": `${this.props.height}vh`
            }}>
                {[...Array(this.props.cardNum).keys()].map(ii =>
                    <UnderCard
                        background={`linear-gradient(90deg, rgba(255,255,255,0.05), rgba(255,255,255,0)),linear-gradient(90deg, #111e34, #111e34)`}
                        text={this.props.labels[ii]}
                        key={ii}
                        onClick={(e) => this.props.onClick(e, this.props.id)}
                        visibility={this.props.visibility}
                        z={this.props.active ? '1' : '0'}
                        value={this.props.values[this.props.labels[ii]]}
                        units={this.props.units}
                    />)}
            </div>
        )
    }
}