import { useEffect, useState } from 'react'
import UserCard from '../components/UserCard'
import UserCardHolder from '../components/UserCardHolder'
import '../SettingsStyle.css'
import SettingsDropdown from '../components/SettingsDropdown'

function Settings(props) {

    useEffect(() => { props.setPage() }, [])

    const [active, setActive] = useState('')
    const [oldActive, setOldActive] = useState('')

    const handleClick = (id) => {
        console.log(id)
        setActive(id)
        setOldActive(id)
    }

    const getActive = (id) => active === id || oldActive === id

    const getOpen = (id) => active === id
    
    return (
        <div className="LogsScreen">
            <div className='RightScreen'>
                <div className='rightSection'>
                    <div className='sectionLabel'>
                        Accounts
                    </div>
                    <UserCardHolder>
                        <UserCard name="Kyle Thompson" email="kyle@maybellquantum.com" role="Owner" />
                        <UserCard name="Michelle Liu" email="michelle@maybellquantum.com" role="User" />
                    </UserCardHolder>
                    <div className='sectionLabel'>
                        <div className='boxed'>
                            + Add Account
                        </div>
                    </div>
                </div>

                <div className='leftSection'>
                    <div className='sectionLabel'>
                        Units
                    </div>
                    <SettingsDropdown label={"Temperature Unit"} option={"Kelvin (K)"} active={getActive("temp")} open={getOpen("temp")} onClick={() => handleClick("temp")} />
                    <SettingsDropdown label={"Pressure Unit"} option={"Millibar (mBar)"} active={getActive("pressure")} open={getOpen("pressure")} onClick={() => handleClick("pressure")} />
                    <SettingsDropdown label={"Flow Rate Unit"} option={"Millimole per second (mmol/s)"} active={getActive("flow")} open={getOpen("flow")} onClick={() => handleClick("flow")} />
                    <SettingsDropdown label={"Power Unit"} option={"Watt (W)"} active={getActive("power")} open={getOpen("power")} onClick={() => handleClick("power")} />

                </div>
                <div className='vLineCenter' />
                <div className='hLineCenter' />
                {/* <div className='BackgroundBlur' style={{
                    opacity: active === '' ? 0 : 1,
                    pointerEvents: active === '' ? 'none' : 'auto'
                }} onClick={() => { setActive('') }}></div> */}
            </div>
        </div >
    )
}

export default Settings