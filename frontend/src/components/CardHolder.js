
import React, { Component } from 'react';
import Card from './Card.js'
import UnderCardHolder from './UnderCardHolder'
import serverParameters from '../data/serverParameters.json';

const dataHost = serverParameters['Data_Host']

async function getValues() {
    const values = fetch('http://98.43.65.223:8000/values', {
        method: 'GET'
    }).then(data => data.json())
        .then(json => { return json })


}

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


export default class CardHolder extends Component {
    constructor(props) {
        super(props);
        this.cardNum = 7

        this.state = {}
        this.open = false
        this.fadesList = Array(this.cardNum).fill(false);
        this.cardLabels = [
            "",
            "CURRENT PRESSURE - ",
            "CURRENT TEMPERATURE - ",
            "TARGET TEMPERATURE ",
            "CIRCULATION RATE ",
            "",
            ""
        ]
        this.units = [
            "",
            "PSI",
            "K",
            "K",
            "SCFM"
        ]
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
            underLabels: this.underCardLabels
        }

        //this.gradientList = generateGradient([23, 28, 66, 0], [23, 28, 66, 1], this.cardNum)
        this.gradientList = generateGradient([0, 0, 0, 0.2], [0, 0, 0, 0], this.cardNum)
        this.underGradients = [...Array(this.underCardLabels.length).keys()].map(
            (ii) =>
                this.underCardLabels[ii].length ? generateGradient([255, 255, 255, 0.0], [255, 255, 255, 0.00], this.underCardLabels[ii].length) : ""

        )

    }

    updateValues = () => {
        fetch(`${dataHost}/values`, {
            method: 'GET'
        }).then(data => data.json())
            .then(json => {
                //console.log(json)
                for (var key in json) {
                    this.values[key] = json[key]
                }
                this.setState({ values: this.values })
            }).catch(e => { console.log("failed to get values") })
        //const values = getValues()
    }

    componentDidMount() {
        this.updateValues()

        setInterval(
            () => {
                this.updateValues()
            }, 20000
        )
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
        const fade = this.state.fade

        return (
            <div className='cardholder'>
                {/* {this.open ? this.underCardHolders[this.activeUnderCardHolder] : ''} */}
                {[...Array(this.underCardNums.length).keys()].map(
                    ii =>
                        <UnderCardHolder
                            key={`UC${ii}`}
                            id={ii}
                            cardNum={this.underCardNums[ii]}
                            visibility={this.state.visibility[ii]}
                            top={ii * this.totalHeight / (this.cardNum + this.underCardNums[ii])}
                            height={this.totalHeight * this.underCardNums[ii] / (this.cardNum + this.underCardNums[ii])}
                            active={ii === this.activeCard ? true : false}
                            labels={this.state.underLabels[ii]}
                            onClick={this.onUnderChildClick}
                            values={this.getUnderCardValues(ii)}
                            background={this.underGradients[ii]}
                            units={this.units[ii]}


                        />
                )}
                {[...Array(this.cardNum).keys()].map(ii =>
                    <Card
                        background={`${this.gradientList[ii]},linear-gradient(90deg, #1f3863, #111e34)`}
                        text={`${this.cardLabels[ii]}${this.state.active[ii] ? this.state.active[ii] : ""}`}
                        key={ii}
                        onClick={this.onChildClick}
                        id={ii}
                        fade={this.state.fades[ii]}
                        padding={this.totalHeight * this.underCardNums[ii] / (this.cardNum + this.underCardNums[ii])}
                        value={this.state.active[ii] ? this.state.values[this.state.active[ii]] : ""}
                        units={this.units[ii]}
                    />
                )}
            </div>
        )
    }
}