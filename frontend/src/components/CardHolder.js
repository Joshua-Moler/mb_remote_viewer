
import React, { Component } from 'react';
import Card from './Card.js'
import UnderCardHolder from './UnderCardHolder'
import serverParameters from '../data/serverParameters.json';

const backendHost = serverParameters['Backend_Host']

function generateGradient(startColor, endColor, chunks) {

    var gradientList = []
    for (var ii = 0; ii < chunks; ii++) {
        var chunkStartColor = []
        var chunkEndColor = []
        for (var jj = 0; jj < startColor.length; jj++) {
            chunkStartColor.push(ii / (chunks) * (endColor[jj] - startColor[jj]) + startColor[jj])
            chunkEndColor.push((ii + 1) / (chunks) * (endColor[jj] - startColor[jj]) + startColor[jj])
        }
        gradientList.push(`linear-gradient(rgba(${[...chunkStartColor]}) 0%, rgba(${[...chunkEndColor]}) 100%)`)
    }

    return gradientList
}

class CardData {
    constructor(label = "", unit = "", activeLabel = "", name = "") {
        this.label = label
        this.unit = unit
        this.activeLabel = activeLabel
        this.name = name
        this.underCardVisibility = "hidden"
        this.underCardValues = {}
        this.fade = false
        this.underGradient = ""
    }
}


export default class CardHolder extends Component {
    constructor(props) {
        super(props);
        this.cardNum = 7
        this.open = false
        const cardNames = {
            0: "STATUS",
            1: "TEMPERATURES",
            2: "PRESSURES",
            3: "SETPOINT",
            4: "FLOW"
        }
        const cardLabels = {
            0: "STATUS",
            1: "CURRENT TEMPERATURE - ",
            2: "CURRENT PRESSURE - ",
            3: "TARGET TEMPERATURE ",
            4: "CIRCULATION RATE ",
        }
        const units = {
            1: "K", 2: "mBar", 3: "K", 4: "L/m"
        }

        this.cards = Object.fromEntries([...Array(this.cardNum).keys()].map((ii) => {

            let card = new CardData()
            if (cardLabels[ii]) card.label = cardLabels[ii]
            if (units[ii]) card.unit = units[ii]
            let name = cardNames[ii] ? cardNames[ii] : String(ii)
            card.name = name
            return [ii, card]

        }))
        this.totalHeight = 100
        this.activeCard = 1
        this.state = this.cards
        this.gradientList = generateGradient([0, 0, 0, 0.2], [0, 0, 0, 0], this.cardNum)
    }

    componentDidMount() {
        this.updateValues()

        this.interval = setInterval(
            () => {
                this.updateValues()
            }, 20000
        )

    }

    componentWillUnmount() {
        clearInterval(this.interval)
    }

    updateValues = () => {
        fetch(`${backendHost}/values`, {
            method: 'GET',
            credentials: 'include'
        }).then(data => data.json())
            .then(json => {
                console.log(json)
                for (const card in this.cards) {
                    if (json[this.cards[card].name]) {
                        this.cards[card].underCardValues = JSON.parse(JSON.stringify(json[this.cards[card].name]))
                        const dataLength = Object.keys(json[this.cards[card].name]).length

                        if (this.cards[card].activeLabel === '')
                            this.cards[card].activeLabel = dataLength ? Object.keys(json[this.cards[card].name])[dataLength - 1] : ""

                        this.cards[card].underGradient = [...Array(Object.keys(this.cards[card].underCardValues).length).keys()].map(
                            (ii) =>
                                Object.keys(this.cards[card].underCardValues).length ? generateGradient([255, 255, 255, 0.0], [255, 255, 255, 0.00], Object.keys(this.cards[card].underCardValues).length) : ""
                        )
                    }
                }
                this.setState(this.cards)
            }).catch(e => { console.log(e) })

    }

    onChildClick = (e) => {

        if (!this.open && Object.keys(this.cards[e].underCardValues).length > 1) {
            let oldActive = this.activeCard
            this.cards[oldActive].underCardVisibility = "hidden"
            this.activeCard = e
            this.cards[e].fade = !this.cards[e].fade

            this.cards[e].underCardVisibility = "visible"

            this.setState({
                [e]: this.cards[e],
                [oldActive]: this.cards[oldActive]
            })
        }
        else {

            this.cards[this.activeCard].fade = false
            this.setState({
                [e]: this.cards[e]
            })
        }
        if (this.open || Object.keys(this.cards[e].underCardValues).length > 1) {
            this.open = !this.open
        }
    }

    onUnderChildClick = (underCard, holder) => {

        if (this.open) {

            this.cards[holder].activeLabel = underCard
            this.cards[holder].fade = false
            this.open = !this.open
            this.setState({
                [holder]: this.cards[holder]
            })




        }

    }

    render() {
        //console.log(this.state[1].underCardValues[this.state[1].activeLabel] ? this.state[1].underCardValues[this.state[1].activeLabel] : "", this.state[1].activeLabel)
        return (
            <div className={`cardholder${this.props.embedded ? " embedded" : ""}`}>
                {/* {this.open ? this.underCardHolders[this.activeUnderCardHolder] : ''} */}
                {Object.keys(this.state).map(
                    ii =>
                        <UnderCardHolder
                            key={`UC${ii}`}
                            id={ii}
                            cardNum={Object.keys(this.state[ii].underCardValues).length}
                            visibility={this.state[ii].underCardVisibility}
                            top={ii * this.totalHeight / (Object.keys(this.state).length + Object.keys(this.state[ii].underCardValues).length - 1)}
                            height={this.totalHeight * (Object.keys(this.state[ii].underCardValues).length - 1) / (Object.keys(this.state).length + Object.keys(this.state[ii].underCardValues).length - 1)}
                            active={this.state[ii].fade}
                            labels={Object.keys(this.state[ii].underCardValues)}
                            onClick={this.onUnderChildClick}
                            values={this.state[ii].underCardValues}
                            background={this.state[ii].underGradient}
                            units={this.state[ii].unit}
                            embedded={this.props.embedded}
                            omit={this.state[ii].activeLabel}


                        />
                )}

                {Object.keys(this.state).map(ii =>
                    <Card
                        background={`${this.gradientList[ii]},linear-gradient(90deg, #1f3863, #111e34)`}
                        text={`${this.state[ii].label}${this.state[ii].activeLabel}`}
                        key={ii}
                        onClick={this.onChildClick}
                        id={ii}
                        fade={this.state[ii].fade}
                        padding={this.totalHeight * (Object.keys(this.state[ii].underCardValues).length - 1) / (Object.keys(this.state).length + Object.keys(this.state[ii].underCardValues).length - 1)}
                        value={this.state[ii].underCardValues[this.state[ii].activeLabel] ? this.state[ii].underCardValues[this.state[ii].activeLabel] : ""}
                        units={this.state[ii].unit}
                    />
                )}
            </div>
        )
    }
}