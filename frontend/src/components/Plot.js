import React, { Component } from 'react';

export default class Plot extends Component {
    constructor(props) {
        super(props);

        this.state = { param: Math.random() }
    }


    componentDidMount() {

        setInterval(
            () => {
                this.setState({ param: Math.random() })
            }, 30000
        )
    }
    render() {

        return (
            <div style={{
                "backgroundImage": `url('http://98.43.65.223:8000/Plot/${this.state.param}')`,
                "backgroundSize": 'contain',
                "preserveAspectRatio": "none",
                "imageRendering": "crisp-edges",
                "backgroundRepeat": "no-repeat",
                "height": "100%",
                "width": "100%",
                "backgroundPosition": "center",

            }}>

            </div>
        );
    }
}