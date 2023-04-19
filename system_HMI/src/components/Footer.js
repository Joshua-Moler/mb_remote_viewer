import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import useToken from '../usePermissions';


export default class Footer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <footer className={`App-footer${this.props.embedded ? " embedded" : ""}`}>

                <Link className={`footerButton${this.props.active === 'Home' ? ' uline' : ''}`} to='/'>Home</Link>
                <Link className={`footerButton${this.props.active === 'Logs' ? ' uline' : ''}`} to='/Logs'>Log</Link>
                <Link className={`footerButton${this.props.active === 'Control' ? ' uline' : ''}`} to='/Control'>Control</Link>
                <button
                    className="footerButton"
                    onClick={() => this.props.logout()}
                >
                    Logout
                </button>
            </footer>
        )
    }
}


