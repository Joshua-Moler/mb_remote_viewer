import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import useToken from '../useToken';


export default class Footer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <footer className="App-footer">

                <Link className={`footerButton${this.props.active === 'Home' ? ' uline' : ''}`} to='/'>Test</Link>
                <Link className={`footerButton${this.props.active === 'Logs' ? ' uline' : ''}`} to='/Logs'>Log</Link>
                <Link className={`footerButton${this.props.active === 'Account' ? ' uline' : ''}`} to='/Account'>Account</Link>
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


