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
    constructor(label = "", unit = "", activeLabel = "", name = "") {
        this.label = label
        this.unit = unit
        this.activeLabel = activeLabel
        this.underCardVisibility = "hidden"
        this.underCardValues = {}
        this.fade = false
        this.underGradient = ""
    }
}


function getInitialCards(cardNum, values) {
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
    console.log('got cards')
    return cards

}


function CardHolder(props) {

    let cardNum = 7
    let open = false
    let totalHeight = 100
    let activeCard = 1

    let cards = getInitialCards(cardNum, props.values)

    let gradientList = generateGradient([0, 0, 0, 0.2], [0, 0, 0, 0], cardNum)

    let onChildClick = (e) => {

        if (!open && Object.keys(cards[e].underCardValues).length > 1) {
            let newCards = { ...cards }
            let oldActive = activeCard
            newCards[oldActive].underCardVisibility = 'hidden'
            activeCard = e
            newCards[e].fade = !newCards[e].fade
            newCards[e].underCardVisibility = 'visible'

        }
        else {
            let newCards = { ...cards }
            newCards[activeCard].fade = false

        }
        if (open || Object.keys(cards[e].underCardValues).length > 1) {
            open = !open
        }


    }

    let onUnderChildClick = (underCard, holder) => {
        if (open) {
            cards[holder].activeLabel = underCard
            cards[holder].fade = false
            open = !open
        }
    }

    return (

        <div className={`cardholder${props.embedded ? " embedded" : ""}`}>
            {/* {open ? underCardHolders[activeUnderCardHolder] : ''} */}
            {Object.keys(cards).map(
                ii =>
                    <UnderCardHolder
                        key={`UC${ii}`}
                        id={ii}
                        cardNum={Object.keys(cards[ii].underCardValues).length}
                        visibility={cards[ii].underCardVisibility}
                        top={ii * totalHeight / (Object.keys(cards).length + Object.keys(cards[ii].underCardValues).length - 1)}
                        height={totalHeight * (Object.keys(cards[ii].underCardValues).length - 1) / (Object.keys(cards).length + Object.keys(cards[ii].underCardValues).length - 1)}
                        active={cards[ii].fade}
                        labels={Object.keys(cards[ii].underCardValues)}
                        onClick={onUnderChildClick}
                        values={cards[ii].underCardValues}
                        background={cards[ii].underGradient}
                        units={cards[ii].unit}
                        embedded={props.embedded}
                        omit={cards[ii].activeLabel}


                    />
            )}

            {Object.keys(cards).map(ii =>
                <Card
                    background={`${gradientList[ii]},linear-gradient(90deg, #1f3863, #111e34)`}
                    text={`${cards[ii].label}${cards[ii].activeLabel}`}
                    key={ii}
                    onClick={onChildClick}
                    id={ii}
                    fade={cards[ii].fade}
                    padding={totalHeight * (Object.keys(cards[ii].underCardValues).length - 1) / (Object.keys(cards).length + Object.keys(cards[ii].underCardValues).length - 1)}
                    value={cards[ii].underCardValues[cards[ii].activeLabel] ? cards[ii].underCardValues[cards[ii].activeLabel] : ""}
                    units={cards[ii].unit}
                />
            )}
        </div>

    )


}

export default CardHolder