import React, { useState } from 'react';
import Card from './Card.js'
import UnderCardHolder from './UnderCardHolder.js'
import serverParameters from '../data/serverParameters.json'

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
    constructor(label = "", unit = "", name = '') {
        this.label = label
        this.unit = unit
        this.underCardValues = {}
        this.underGradient = ""
        this.name = name
    }
}


function getInitialCards(cardNum, values) {
    const cardNames = {
        0: "STATUS",
        1: "TEMPERATURES",
        2: "PRESSURES",
        3: "SETPOINT",
        4: "FLOWS"
    }

    const cardLabels = {
        0: "STATUS",
        1: "CURRENT TEMPERATURE - ",
        2: "CURRENT PRESSURE - ",
        3: "TARGET TEMPERATURE ",
        4: "CIRCULATION RATE ",
    }

    const units = {
        1: "K",
        2: "mBar",
        3: "K",
        4: "L/m"
    }
    let cards = Object.fromEntries([...Array(cardNum).keys()].map((ii) => {

        let card = new CardData()
        if (cardLabels[ii]) card.label = cardLabels[ii]
        if (units[ii]) card.unit = units[ii]
        let name = cardNames[ii] ? cardNames[ii] : String(ii)
        card.name = name
        return [ii, card]
    }))

    for (const card in cards) {
        if (values[cards[card].name] != undefined) {
            cards[card].underCardValues = JSON.parse(JSON.stringify(values[cards[card].name]))
            const dataLength = Object.keys(values[cards[card].name]).length

            if (cards[card].activeLabel === '')
                cards[card].activeLabel = dataLength ? Object.keys(values[cards[card].name])[dataLength - 1] : ""

            cards[card].underGradient = [...Array(Object.keys(cards[card].underCardValues).length).keys()].map(
                (ii) => Object.keys(cards[card].underCardValues).length ? generateGradient([255, 255, 255, 0.0], [255, 255, 255, 0.0], Object.keys(cards[card].underCardValues).length) : ""
            )
        }
    }
    return cards

}


function CardHolder(props) {

    let cardNum = 7
    let [open, setOpen] = useState(false)
    let totalHeight = 100
    let [activeCard, setActiveCard] = useState(1)
    let [structure, setStructure] = useState(Array(cardNum).fill({ fade: false, activeLabel: '', underCard: 'hidden' }))

    let cards = getInitialCards(cardNum, props.values)

    let newStructure = JSON.parse(JSON.stringify(structure))
    let changed = false
    for (let card in cards) {
        let oldActiveLabel = newStructure[card].activeLabel
        let dataLength = Object.keys(cards[card].underCardValues).length
        let newActiveLabel = dataLength && oldActiveLabel === '' ? Object.keys(props.values[cards[card].name])[dataLength - 1] : oldActiveLabel

        if (oldActiveLabel != newActiveLabel) {
            changed = true
            newStructure[card].activeLabel = newActiveLabel
        }

    }
    if (changed)
        setStructure(newStructure)

    let gradientList = generateGradient([0, 0, 0, 0.2], [0, 0, 0, 0], cardNum)

    let onChildClick = (e) => {
        if (!open && Object.keys(cards[e].underCardValues).length > 1) {
            let newStructure = JSON.parse(JSON.stringify(structure))

            let oldActive = activeCard
            newStructure[oldActive].underCard = 'hidden'
            setActiveCard(e)
            newStructure[e].fade = !newStructure[e].fade
            newStructure[e].underCard = 'visible'

            setStructure(newStructure)

        }
        else {
            let newStructure = JSON.parse(JSON.stringify(structure))
            newStructure[activeCard].fade = false

            setStructure(newStructure)

        }
        if (open || Object.keys(cards[e].underCardValues).length > 1) {
            setOpen(prevState => !prevState)
        }

    }

    let onUnderChildClick = (underCard, holder) => {
        if (open) {

            let newStructure = JSON.parse(JSON.stringify(structure))

            newStructure[holder].activeLabel = underCard
            newStructure[holder].fade = false
            setStructure(newStructure)
            setOpen(prevState => !prevState)
        }
    }

    return (

        < div className={`cardholder${props.embedded ? " embedded" : ""}`
        }>
            {/* {open ? underCardHolders[activeUnderCardHolder] : ''} */}
            {
                Object.keys(cards).map(
                    ii =>
                        <UnderCardHolder
                            key={`UC${ii}`}
                            id={ii}
                            cardNum={Object.keys(cards[ii].underCardValues).length}
                            visibility={structure[ii].underCard}
                            top={ii * totalHeight / (Object.keys(cards).length + Object.keys(cards[ii].underCardValues).length - 1)}
                            height={totalHeight * (Object.keys(cards[ii].underCardValues).length - 1) / (Object.keys(cards).length + Object.keys(cards[ii].underCardValues).length - 1)}
                            active={structure[ii].fade && open}
                            labels={Object.keys(cards[ii].underCardValues)}
                            onClick={onUnderChildClick}
                            values={cards[ii].underCardValues}
                            background={cards[ii].underGradient}
                            units={cards[ii].unit}
                            embedded={props.embedded}
                            omit={structure[ii].activeLabel}


                        />
                )
            }

            {
                Object.keys(cards).map(ii =>
                    <Card
                        background={`${gradientList[ii]},linear-gradient(90deg, #1f3863, #111e34)`}
                        text={`${cards[ii].label}${structure[ii].activeLabel}`}
                        key={ii}
                        onClick={onChildClick}
                        id={ii}
                        fade={structure[ii].fade && open}
                        padding={totalHeight * (Object.keys(cards[ii].underCardValues).length - 1) / (Object.keys(cards).length + Object.keys(cards[ii].underCardValues).length - 1)}
                        value={cards[ii].underCardValues[structure[ii].activeLabel] ? cards[ii].underCardValues[structure[ii].activeLabel] : ""}
                        units={cards[ii].unit}
                    />
                )
            }

        </div >

    )


}

export default CardHolder