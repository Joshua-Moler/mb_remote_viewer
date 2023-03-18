
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
        this.underCardVisibility = false
        this.underCardValues = {}
        this.isActive = false
        this.fade = false
        this.underGradient = ""
    }
}


export default class CardHolder extends Component {
    constructor(props) {
        super(props);
        this.cardNum = 7

        this.open = false
        this.fadesList = Array(this.cardNum).fill(false);
        const cardNames = {
            0: "STATUS",
            1: "TEMPERATURES",
            2: "PRESSURES",
            3: "SETPOINT",
            4: "FLOW"
        }
        const cardLabels = {
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

        this.underCardNums = [0, 5, 5]
        this.underCardLabels = [
            [],
            [
                "P2", "P3", "P4", "P5", "P6"
            ],
            [
                "PRP", "RGP", "CFP", "STP", "ICP"
            ]
        ]
        this.correctOrders = [
            [],
            [
                "P1", "P2", "P3", "P4", "P5", "P6"
            ],
            [
                "PRP", "RGP", "CFP", "STP", "ICP", "MXP"
            ]
        ]
        this.activeLabels = [
            "STATUS", "P1", "MXP", "SETPOINT", "FLOW", ""
        ]

        this.totalHeight = 100

        this.underCardVisibility = Array(2).fill("hidden")
        this.activeCard = 0
        this.values = {
            'P1': 0,
            'P2': 0,
            'P3': 0,
            'P4': 0,
            'P5': 0,
            'P6': 0,
            'PRP': 0,
            'RGP': 0,
            'CFP': 0,
            'STP': 0,
            'ICP': 0,
            'MXP': 0
        }
        this.state = {
            fades: [...this.fadesList],
            visibility: [...this.underCardVisibility],
            values: this.values,
            active: this.activeLabels,
            underLabels: this.underCardLabels,
        }

        //this.gradientList = generateGradient([23, 28, 66, 0], [23, 28, 66, 1], this.cardNum)
        this.gradientList = generateGradient([0, 0, 0, 0.2], [0, 0, 0, 0], this.cardNum)
        this.underGradients = [...Array(this.underCardLabels.length).keys()].map(
            (ii) =>
                this.underCardLabels[ii].length ? generateGradient([255, 255, 255, 0.0], [255, 255, 255, 0.00], this.underCardLabels[ii].length) : ""

        )

    }

    updateValues = () => {
        fetch(`${backendHost}/values`, {
            method: 'GET'
        }).then(data => data.json())
            .then(json => {

                for (const card in this.cards) {
                    console.log(this.cards[card])
                    if (json[this.cards[card].name]) {

                        this.cards[card].underCardValues = JSON.parse(JSON.stringify(json[this.cards[card].name]))

                        const dataLength = Object.keys(json[this.cards[card].name]).length

                        this.cards[card].activeLabel = dataLength ? Object.keys(json[this.cards[card].name])[dataLength - 1] : ""

                        this.cards[card].underGradient = [...Array(Object.keys(this.cards[card].underCardValues).length).keys()].map(
                            (ii) =>
                                Object.keys(this.cards[card].underCardValues).length ? generateGradient([255, 255, 255, 0.0], [255, 255, 255, 0.00], Object.keys(this.cards[card].underCardValues).length) : ""
                        )


                    }

                }


                console.log(this.cards)

                for (var key in json) {
                    this.values[key] = json[key]
                }
                this.setState({ values: this.values })
            }).catch(e => { console.log(e) })
        //const values = getValues()
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

    onChildClick = (e) => {
        if (!this.open && this.underCardNums[e]) {
            this.activeCard = e
            this.fadesList[e] = !this.fadesList[e]
            this.underCardVisibility[e] = "visible"
            this.setState({
                fades: [...this.fadesList],
                visibility: [...this.underCardVisibility]
            })
        }
        else {
            this.fadesList[this.activeCard] = false
            this.underCardVisibility[this.activeCard] = "hidden"
            this.setState({
                fades: this.fadesList
            })
        }
        if (this.open || this.underCardNums[e]) {
            this.open = !this.open
        }
    }

    onUnderChildClick = (underCard, holder) => {
        if (this.open) {
            for (var ii = 0; ii < this.underCardLabels[holder].length; ii++) {
                if (this.underCardLabels[holder][ii] === underCard) {
                    this.underCardLabels[holder][ii] = this.activeLabels[holder]
                    break
                }
            }
            var newUnderCardLabels = Array(this.underCardLabels[holder].length).fill("")
            var count = 0
            for (var ii = 0; ii < this.correctOrders[holder].length; ii++) {
                for (var jj = 0; jj < this.underCardLabels[holder].length; jj++) {
                    if (this.underCardLabels[holder][jj] === this.correctOrders[holder][ii]) {
                        newUnderCardLabels[count++] = this.underCardLabels[holder][jj]
                    }
                }
            }
            this.underCardLabels[holder] = newUnderCardLabels
            this.activeLabels[holder] = underCard
            this.setState({
                active: this.activeLabels,
                underLabels: this.underCardLabels
            })

            this.fadesList[this.activeCard] = false
            this.underCardVisibility[this.activeCard] = "hidden"
            this.setState({
                fades: this.fadesList
            })
            this.open = !this.open

        }
    }

    getUnderCardValues = (ii) => {
        if (!this.underCardLabels[ii]) return {}
        var v = {}
        for (var jj = 0; jj < this.underCardLabels[ii].length; jj++) {
            var label = this.underCardLabels[ii][jj]
            v[label] = this.values[label]
        }

        return v
    }


    render() {

        return (
            <div className={`cardholder${this.props.embedded ? " embedded" : ""}`}>
                {/* {this.open ? this.underCardHolders[this.activeUnderCardHolder] : ''} */}
                {Object.keys(this.cards).map(
                    ii =>
                        <UnderCardHolder
                            key={`UC${ii}`}
                            id={ii}
                            cardNum={this.cards[ii].underCardValues.length}
                            visibility={this.cards[ii].underCardVisibility}
                            top={ii * this.totalHeight / (this.cards.length + this.cards[ii].underCardValues.length)}
                            height={this.totalHeight * this.cards[ii].underCardValues.length / (this.cards.length + this.cards[ii].underCardValues.length)}
                            active={this.cards[ii].isActive}
                            labels={Object.keys(this.cards[ii].underCardValues)}
                            onClick={this.onUnderChildClick}
                            values={this.cards[ii].underCardValues}
                            background={this.cards[ii].underGradient}
                            units={this.cards[ii].unit}
                            embedded={this.props.embedded}


                        />
                )}
                {Object.keys(this.cards).map(ii =>
                    <Card
                        background={`${this.gradientList[ii]},linear-gradient(90deg, #1f3863, #111e34)`}
                        text={`${this.cards[ii].label}${this.cards[ii].activeLabel}`}
                        key={ii}
                        onClick={this.onChildClick}
                        id={ii}
                        fade={this.cards[ii].fade}
                        padding={this.totalHeight * this.cards[ii].underCardValues.length / (this.cards.length + this.cards[ii].underCardValues.length)}
                        value={this.cards[ii].isActive ? this.cards[ii].activeLabel : ""}
                        units={this.cards[ii].unit}
                    />
                )}
            </div>
        )
    }
}