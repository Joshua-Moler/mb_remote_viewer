
function UserCard(props) {

    return (

        <div className='userCard'>

            <div className='cardLeft'>
                <div className='userName'>
                    {props.name}
                </div>
                <div className='userEmail'>
                    {props.email}
                </div>
            </div>

            <div className='cardRight'>
                <div className={`${props.role.toLowerCase()}Tag`}>
                    {props.role}
                </div>
                <div className='userEdit'>
                    EDIT
                </div>
            </div>

        </div>

    )

}

export default UserCard