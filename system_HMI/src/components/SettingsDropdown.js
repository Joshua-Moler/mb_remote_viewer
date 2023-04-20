
function SettingsDropdown(props) {

    const options = (children) => {

        if (props.open)
            return (
                <div style={{ position: 'absolute', width: "100%", overflow: "hidden", transition: "max-height 0.25s", maxHeight: '200px' }}>
                    <div className="settingsDropdownTop" style={{ position: 'relative', transition: "transform 0.25s", transform: "translateY(0px)", float: "inline-start" }}>
                        <div className="settingsDropdownItem">
                            hello
                        </div>

                    </div>
                    <div className="settingsDropdownTop" style={{ transition: "transform 0.25s", transform: "translateY(0px)" }}>
                        <div className="settingsDropdownItem">
                            hello
                        </div>

                    </div>
                </div>
            )
        return

    }

    return (
        <div className="settingsDropdownBase" style={{ zIndex: props.active ? 101 : 1 }}>
            <div className="settingsDropdownLabel">
                {props.label}
            </div>
            <div className="settingsDropdownTop" onClick={props.onClick}>
                <div className="settingsDropdownItem">
                    {props.option}
                </div>
                <div className="settingsDropdownItem" style={{ rotate: props.open ? "180deg" : "0deg" }}>
                    <svg width="22" height="22" viewBox="0 0 22 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 1L11 11L21 1" stroke="#F2EAFA" strokeWidth="2" />
                    </svg>
                </div>
            </div>
            {options()}
        </div >

    )

}

export default SettingsDropdown